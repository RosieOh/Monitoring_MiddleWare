import json
import re
from datetime import datetime
from pathlib import Path


class LogAnalyzer:
    def __init__(self):
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        self.log_patterns = {
            'error': r'ERROR|CRITICAL|FATAL',
            'warning': r'WARNING|WARN',
            'info': r'INFO'
        }
        
    def parse_log_file(self, file_path):
        logs = []
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    parsed = self.parse_log_line(line)
                    if parsed:
                        logs.append(parsed)
        except Exception as e:
            print(f"Error parsing log file: {e}")
        return logs

    def parse_log_line(self, line):
        try:
            # 기본적인 로그 형식 파싱
            # 예: "2024-02-28 12:34:56 [INFO] Message"
            match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[(\w+)\] (.*)', line)
            if match:
                timestamp, level, message = match.groups()
                return {
                    'timestamp': timestamp,
                    'level': level,
                    'message': message,
                    'source': 'system'
                }
        except Exception as e:
            print(f"Error parsing log line: {e}")
        return None

    def search_logs(self, query=None, start_time=None, end_time=None, level=None, page=1, per_page=50):
        all_logs = []
        
        # 로그 파일들을 읽어서 검색 조건에 맞는 로그 수집
        for log_file in self.log_dir.glob('*.log'):
            logs = self.parse_log_file(log_file)
            all_logs.extend(logs)

        # 필터링
        filtered_logs = all_logs
        if query:
            filtered_logs = [log for log in filtered_logs 
                           if query.lower() in log['message'].lower()]
        if level and level != 'all':
            filtered_logs = [log for log in filtered_logs 
                           if log['level'].lower() == level.lower()]
        if start_time:
            start = datetime.fromisoformat(start_time)
            filtered_logs = [log for log in filtered_logs 
                           if datetime.fromisoformat(log['timestamp']) >= start]
        if end_time:
            end = datetime.fromisoformat(end_time)
            filtered_logs = [log for log in filtered_logs 
                           if datetime.fromisoformat(log['timestamp']) <= end]

        # 정렬 (최신 순)
        filtered_logs.sort(key=lambda x: x['timestamp'], reverse=True)

        # 페이지네이션
        total = len(filtered_logs)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_logs = filtered_logs[start_idx:end_idx]

        return {
            'logs': paginated_logs,
            'total': total,
            'page': page,
            'per_page': per_page
        }

    def add_log(self, level, message, source='system'):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = {
            'timestamp': timestamp,
            'level': level.upper(),
            'message': message,
            'source': source
        }
        
        # 로그를 파일에 저장
        log_file = self.log_dir / f"{datetime.now().strftime('%Y%m%d')}.log"
        with open(log_file, 'a') as f:
            f.write(f"{timestamp} [{level.upper()}] {message}\n")
        
        return log_entry

    def get_log_statistics(self):
        """로그 통계 정보 반환"""
        stats = {
            'error': 0,
            'warning': 0,
            'info': 0,
            'total': 0
        }
        
        for log_file in self.log_dir.glob('*.log'):
            logs = self.parse_log_file(log_file)
            for log in logs:
                level = log['level'].lower()
                if level in stats:
                    stats[level] += 1
                stats['total'] += 1
                
        return stats 