import csv
import time
from datetime import datetime
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
    def get_all_metrics(self):
        metrics = {
            'cpu': self.calculate_cpu_average(),
            'memory': self.get_memory_info(),
            'disk_io': self.calculate_disk_io(),
            'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.save_metrics_to_log(metrics)  # 메트릭을 로그에 저장
        return metrics 