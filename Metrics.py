import time
from datetime import datetime

import psutil
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
# 모든 도메인에서의 접근을 허용하되, 특정 메서드만 허용
CORS(app, resources={
    r"/api/*": {
        "origins": "*",                     # 실제 운영환경에서는 특정 도메인으로 제한하는 것이 좋습니다
        "methods": ["GET"],                 # GET 메서드만 허용
        "allow_headers": ["Content-Type"]
    }
})

last_disk_io = psutil.disk_io_counters()
last_disk_time = time.time()
bandwidth_samples = []  # 샘플 저장 리스트
SAMPLE_DURATION = 300  # 5분 (300초)

# CPU 샘플 저장을 위한 전역 변수
cpu_samples = []
CPU_SAMPLE_DURATION = 60  # 1분 (60초)
last_cpu_time = time.time()

def calculate_cpu_average():
    global cpu_samples, last_cpu_time
    current_time = time.time()
    
    # CPU 사용률 샘플 추가
    cpu_samples.append({
        'time': current_time,
        'usage': psutil.cpu_percent(interval=None)
    })
    
    # 1분이 지난 샘플 제거
    cpu_samples = [
        sample for sample in cpu_samples
        if current_time - sample['time'] <= CPU_SAMPLE_DURATION
    ]
    
    # 1분 평균 계산
    if cpu_samples:
        avg_cpu = sum(sample['usage'] for sample in cpu_samples) / len(cpu_samples)
        return avg_cpu
    return 0

def calculate_disk_io():
    global last_disk_io, last_disk_time, bandwidth_samples
    try:
        current_disk_io = psutil.disk_io_counters()
        current_time = time.time()
        time_delta = current_time - last_disk_time
        if time_delta > 0:
            # 델타 계산
            read_count_delta = current_disk_io.read_count - last_disk_io.read_count
            write_count_delta = current_disk_io.write_count - last_disk_io.write_count
            # IOPS 계산 (초당 작업 수)
            read_iops = read_count_delta / time_delta if time_delta > 0 else 0
            write_iops = write_count_delta / time_delta if time_delta > 0 else 0
            # 샘플 추가
            bandwidth_samples.append({
                'time': current_time,
                'read_iops': read_iops,
                'write_iops': write_iops
            })
            # 오래된 샘플 제거 (SAMPLE_DURATION 이내의 샘플만 유지)
            bandwidth_samples = [
                sample for sample in bandwidth_samples
                if current_time - sample['time'] <= SAMPLE_DURATION
            ]
            # 5분 평균 IOPS 계산
            avg_read_iops_5min = 0
            avg_write_iops_5min = 0
            if bandwidth_samples:
                total_read_iops = sum(sample['read_iops'] for sample in bandwidth_samples)
                total_write_iops = sum(sample['write_iops'] for sample in bandwidth_samples)
                avg_read_iops_5min = total_read_iops / len(bandwidth_samples)
                avg_write_iops_5min = total_write_iops / len(bandwidth_samples)
            # 전역 변수 업데이트
            last_disk_io = current_disk_io
            last_disk_time = current_time
            return {
                'read_iops': round(avg_read_iops_5min, 2),  # 초당 읽기 작업 수
                'write_iops': round(avg_write_iops_5min, 2)  # 초당 쓰기 작업 수
            }
    except Exception as e:
        print(f"Error in calculate_disk_io: {e}")
        return None
    return None

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    try:
        # CPU 1분 평균 사용률 계산
        cpu_avg = calculate_cpu_average()
        
        # 메모리 정보
        memory = psutil.virtual_memory()
        memory_info = {
            'total_gb': round(memory.total / (1024 * 1024 * 1024), 2),
            'used_gb': round(memory.used / (1024 * 1024 * 1024), 2),
            'usage_percent': memory.percent
        }
        
        # Disk I/O
        disk_io = calculate_disk_io() or {
            'read': 0,
            'write': 0
        }
            
        return jsonify({
            'cpu': round(cpu_avg, 2),  # 1분 평균 CPU 사용률을 소수점 둘째자리까지 표시
            'memory': memory_info,
            'disk_io': disk_io,
            'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # 개발 환경
    app.run(host='0.0.0.0', port=5001, debug=False)
