import csv
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

import psutil


# 메트릭 수집 클래스 추가
class MetricsCollector:
    def __init__(self):
        self.last_disk_io = psutil.disk_io_counters()
        self.last_disk_time = time.time()
        self.bandwidth_samples = []
        self.SAMPLE_DURATION = 300  # 5분
        
        self.cpu_samples = []
        self.CPU_SAMPLE_DURATION = 60  # 1분
        self.last_cpu_time = time.time()
        self.log_data = []
        self.log_file_path = Path("logs")
        self.log_file_path.mkdir(exist_ok=True)
        self.servers = self._load_servers()
        self.alerts = self._load_alerts()
        self.alert_thresholds = {
            'cpu': 80,
            'memory': 90,
            'disk': 85
        }

    def _load_servers(self):
        try:
            with open('config/servers.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {'local': {'name': 'Local Server', 'host': 'localhost'}}

    def _load_alerts(self):
        try:
            with open('config/alerts.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def get_servers(self):
        return self.servers

    def get_alerts(self):
        return self.alerts

    def check_alerts(self, metrics):
        alerts = []
        if metrics['cpu'] > self.alert_thresholds['cpu']:
            alerts.append({
                'type': 'cpu',
                'message': f"CPU usage is high: {metrics['cpu']}%",
                'timestamp': datetime.now().isoformat()
            })
        if metrics['memory']['usage_percent'] > self.alert_thresholds['memory']:
            alerts.append({
                'type': 'memory',
                'message': f"Memory usage is high: {metrics['memory']['usage_percent']}%",
                'timestamp': datetime.now().isoformat()
            })
        return alerts

    # CPU 사용률 계산
    def calculate_cpu_average(self):
        current_time = time.time()
        
        self.cpu_samples.append({
            'time': current_time,
            'usage': psutil.cpu_percent(interval=None)
        })
        
        self.cpu_samples = [
            sample for sample in self.cpu_samples
            if current_time - sample['time'] <= self.CPU_SAMPLE_DURATION
        ]
        
        if self.cpu_samples:
            avg_cpu = sum(sample['usage'] for sample in self.cpu_samples) / len(self.cpu_samples)
            return round(avg_cpu, 2)
        return 0

    def calculate_disk_io(self):
        try:
            current_disk_io = psutil.disk_io_counters()
            current_time = time.time()
            time_delta = current_time - self.last_disk_time

            if time_delta > 0:
                read_count_delta = current_disk_io.read_count - self.last_disk_io.read_count
                write_count_delta = current_disk_io.write_count - self.last_disk_io.write_count
                
                read_iops = read_count_delta / time_delta
                write_iops = write_count_delta / time_delta
                
                self.bandwidth_samples.append({
                    'time': current_time,
                    'read_iops': read_iops,
                    'write_iops': write_iops
                })
                
                self.bandwidth_samples = [
                    sample for sample in self.bandwidth_samples
                    if current_time - sample['time'] <= self.SAMPLE_DURATION
                ]
                
                if self.bandwidth_samples:
                    total_read_iops = sum(sample['read_iops'] for sample in self.bandwidth_samples)
                    total_write_iops = sum(sample['write_iops'] for sample in self.bandwidth_samples)
                    avg_read_iops = total_read_iops / len(self.bandwidth_samples)
                    avg_write_iops = total_write_iops / len(self.bandwidth_samples)
                    
                    self.last_disk_io = current_disk_io
                    self.last_disk_time = current_time
                    
                    return {
                        'read_iops': round(avg_read_iops, 2),
                        'write_iops': round(avg_write_iops, 2)
                    }
        except Exception as e:
            print(f"Error in calculate_disk_io: {e}")
        return {'read_iops': 0, 'write_iops': 0}

    # 메모리 정보 수집
    def get_memory_info(self):
        memory = psutil.virtual_memory()
        return {
            'total_gb': round(memory.total / (1024 * 1024 * 1024), 2),
            'used_gb': round(memory.used / (1024 * 1024 * 1024), 2),
            'usage_percent': memory.percent
        }

    # 메트릭을 로그에 저장하는 함수 추가
    def save_metrics_to_log(self, metrics):
        self.log_data.append(metrics)
        
    # 엑셀 내보내기 함수 추가
    def export_to_csv(self):
        if not self.log_data:
            return None
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = self.log_file_path / f'metrics_log_{timestamp}.csv'
        
        headers = [
            'datetime', 'cpu_usage', 
            'memory_total_gb', 'memory_used_gb', 'memory_usage_percent',
            'disk_read_iops', 'disk_write_iops'
        ]
        
        # 로그 파일 경로 설정
        try:
            with open(file_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                for data in self.log_data:
                    writer.writerow({
                        'datetime': data['datetime'],
                        'cpu_usage': data['cpu'],
                        'memory_total_gb': data['memory']['total_gb'],
                        'memory_used_gb': data['memory']['used_gb'],
                        'memory_usage_percent': data['memory']['usage_percent'],
                        'disk_read_iops': data['disk_io']['read_iops'],
                        'disk_write_iops': data['disk_io']['write_iops']
                    })
            return str(file_path)
        except Exception as e:
            print(f"Error saving CSV: {e}")
            return None

    # 모든 메트릭 수집 함수 추가
    def get_all_metrics(self, server_id='local'):
        metrics = {
            'cpu': self.calculate_cpu_average(),
            'memory': self.get_memory_info(),
            'disk_io': self.calculate_disk_io(),
            'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'server_id': server_id
        }
        
        # 알림 체크 및 저장
        alerts = self.check_alerts(metrics)
        if alerts:
            self.alerts.extend(alerts)
            self._save_alerts()
        
        self.save_metrics_to_log(metrics)
        return metrics

    def _save_alerts(self):
        with open('config/alerts.json', 'w') as f:
            json.dump(self.alerts, f)

    def _get_report_headers(self):
        return [
            'datetime',
            'cpu_usage',
            'memory_total_gb',
            'memory_used_gb',
            'memory_usage_percent',
            'disk_read_iops',
            'disk_write_iops'
        ]

    def _generate_daily_report(self, date):
        """일간 리포트 생성"""
        try:
            daily_data = [entry for entry in self.log_data 
                         if entry['datetime'].startswith(date)]
            return daily_data
        except Exception as e:
            print(f"Error generating daily report: {e}")
            return []

    def _generate_weekly_report(self, date):
        """주간 리포트 생성"""
        try:
            # 선택된 날짜를 기준으로 일주일 데이터 필터링
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            week_start = date_obj - timedelta(days=date_obj.weekday())
            week_end = week_start + timedelta(days=7)
            
            weekly_data = [
                entry for entry in self.log_data
                if week_start <= datetime.strptime(entry['datetime'].split()[0], '%Y-%m-%d') < week_end
            ]
            return weekly_data
        except Exception as e:
            print(f"Error generating weekly report: {e}")
            return []

    def _generate_monthly_report(self, date):
        """월간 리포트 생성"""
        try:
            # 선택된 월의 데이터 필터링
            month = date[:7]  # YYYY-MM
            monthly_data = [entry for entry in self.log_data 
                           if entry['datetime'].startswith(month)]
            return monthly_data
        except Exception as e:
            print(f"Error generating monthly report: {e}")
            return []

    def get_report_list(self):
        """생성된 리포트 목록 반환"""
        try:
            reports = []
            for file in self.log_file_path.glob('report_*.csv'):
                # 파일명에서 정보 추출 (report_type_timestamp.csv)
                filename = file.stem  # 확장자 제외한 파일명
                parts = filename.split('_')
                if len(parts) >= 3:
                    report_type = parts[1]
                    timestamp = '_'.join(parts[2:])
                    reports.append({
                        'id': filename,
                        'type': report_type,
                        'created_at': datetime.strptime(timestamp, '%Y%m%d_%H%M%S').strftime('%Y-%m-%d %H:%M:%S')
                    })
            return sorted(reports, key=lambda x: x['created_at'], reverse=True)
        except Exception as e:
            print(f"Error getting report list: {e}")
            return []

    def get_report_file(self, report_id):
        """특정 리포트 파일 경로 반환"""
        try:
            file_path = self.log_file_path / f'{report_id}.csv'
            return str(file_path) if file_path.exists() else None
        except Exception as e:
            print(f"Error getting report file: {e}")
            return None

    def generate_report(self, date, report_type):
        """리포트 생성 메서드"""
        try:
            # 리포트 데이터 생성
            if report_type == 'daily':
                report_data = self._generate_daily_report(date)
            elif report_type == 'weekly':
                report_data = self._generate_weekly_report(date)
            elif report_type == 'monthly':
                report_data = self._generate_monthly_report(date)
            else:
                raise ValueError(f"Unknown report type: {report_type}")

            if not report_data:
                print(f"No data available for {report_type} report on {date}")
                return None

            # 리포트 파일 생성
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_path = self.log_file_path / f'report_{report_type}_{timestamp}.csv'

            headers = [
                'datetime',
                'cpu_usage',
                'memory_total_gb',
                'memory_used_gb',
                'memory_usage_percent',
                'disk_read_iops',
                'disk_write_iops'
            ]

            with open(file_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                for data in report_data:
                    writer.writerow({
                        'datetime': data['datetime'],
                        'cpu_usage': data['cpu'],
                        'memory_total_gb': data['memory']['total_gb'],
                        'memory_used_gb': data['memory']['used_gb'],
                        'memory_usage_percent': data['memory']['usage_percent'],
                        'disk_read_iops': data['disk_io']['read_iops'],
                        'disk_write_iops': data['disk_io']['write_iops']
                    })

            return str(file_path)

        except Exception as e:
            print(f"Error generating report: {e}")
            raise 