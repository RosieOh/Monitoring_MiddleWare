import json
import logging
import os
import platform
import subprocess
from datetime import datetime
from io import BytesIO
from pathlib import Path

import pandas as pd
import paramiko
import psutil
from flask import Flask, jsonify, render_template, request, send_file
from flask_cors import CORS
from flask_socketio import SocketIO, emit

from log_analyzer import LogAnalyzer
from metrics_collector import MetricsCollector
from network_monitor import NetworkMonitor
from notification_system import NotificationSystem
from performance_analyzer import PerformanceAnalyzer
from process_monitor import ProcessMonitor

app = Flask(__name__)

# CORS 설정을 더 구체적으로 지정
CORS(app, resources={
    r"/api/*": {
        "origins": "*",  # 모든 도메인 허용
        "methods": ["GET", "POST", "OPTIONS"],  # 허용할 HTTP 메서드
        "allow_headers": ["Content-Type", "Authorization"],  # 허용할 헤더
        "supports_credentials": True  # 쿠키/인증 정보 허용
    }
})

app.config['SECRET_KEY'] = 'your-secret-key'

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

metrics_collector = MetricsCollector()

# 시스템 컴포넌트 초기화
notification_system = NotificationSystem(config={})
process_monitor = ProcessMonitor()
network_monitor = NetworkMonitor()
log_analyzer = LogAnalyzer()
performance_analyzer = PerformanceAnalyzer()

socketio = SocketIO(app, cors_allowed_origins="*")

# AWS SSH 연결을 위한 클래스
class SSHClient:
    def __init__(self):
        self.ssh = None
        
    def connect(self, hostname, username, key_path):
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # 키 파일로 접속
            key = paramiko.RSAKey.from_private_key_file(key_path)
            self.ssh.connect(hostname=hostname, username=username, pkey=key)
            return True
        except Exception as e:
            print(f"Connection error: {str(e)}")
            return False
            
    def execute_command(self, command):
        if not self.ssh:
            return "Not connected to server"
        
        try:
            stdin, stdout, stderr = self.ssh.exec_command(command)
            output = stdout.read().decode()
            error = stderr.read().decode()
            return output if output else error
        except Exception as e:
            return f"Error executing command: {str(e)}"

ssh_client = SSHClient()

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/console')
def console():
    return render_template('console.html')

@app.route('/processes')
def processes():
    return render_template('processes.html')

@app.route('/network')
def network():
    return render_template('network.html')

@app.route('/logs')
def logs():
    return render_template('logs.html')

@app.route('/alerts')
def alerts():
    return render_template('alerts.html')

@app.route('/performance')
def performance():
    return render_template('performance.html')

@app.route('/reports')
def reports():
    return render_template('reports.html')

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    try:
        return jsonify(metrics_collector.get_all_metrics()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export-csv', methods=['GET'])
def export_csv():
    try:
        file_path = metrics_collector.export_to_csv()
        if file_path:
            return send_file(
                file_path,
                mimetype='text/csv',
                as_attachment=True,
                download_name=Path(file_path).name
            )
        return jsonify({'error': 'No data available'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/generate', methods=['POST'])
def generate_report():
    try:
        start_date = request.json.get('start_date')
        end_date = request.json.get('end_date')
        report_type = request.json.get('type', 'system')
        
        # 리포트 데이터 생성
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'type': report_type,
            'period': {
                'start': start_date,
                'end': end_date
            },
            'system_status': {
                'cpu': {
                    'percent': psutil.cpu_percent(interval=1),
                    'processes': process_monitor.get_process_list()
                },
                'memory': psutil.virtual_memory()._asdict(),
                'disk': psutil.disk_usage('/')._asdict(),
                'network': network_monitor.get_network_stats()
            },
            'logs': log_analyzer.search_logs(
                start_time=start_date,
                end_time=end_date,
                page=1,
                per_page=1000
            )
        }
        
        # JSON 파일 저장
        report_filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        json_filename = f"{report_filename}.json"
        excel_filename = f"{report_filename}.xlsx"
        
        os.makedirs('reports', exist_ok=True)
        json_path = os.path.join('reports', json_filename)
        excel_path = os.path.join('reports', excel_filename)
        
        # JSON 저장
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
            
        # Excel 생성
        with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
            # CPU 정보
            pd.DataFrame(report_data['system_status']['cpu']['processes']).to_excel(
                writer, sheet_name='Processes', index=False)
            
            # 메모리 정보
            pd.DataFrame([report_data['system_status']['memory']]).to_excel(
                writer, sheet_name='Memory', index=False)
            
            # 디스크 정보
            pd.DataFrame([report_data['system_status']['disk']]).to_excel(
                writer, sheet_name='Disk', index=False)
            
            # 네트워크 정보
            pd.DataFrame([report_data['system_status']['network']]).to_excel(
                writer, sheet_name='Network', index=False)
            
            # 로그 정보
            if report_data['logs'].get('logs'):
                pd.DataFrame(report_data['logs']['logs']).to_excel(
                    writer, sheet_name='Logs', index=False)
            
        return jsonify({
            'success': True,
            'json_filename': json_filename,
            'excel_filename': excel_filename,
            'message': '리포트가 생성되었습니다.'
        })
        
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '리포트 생성 중 오류가 발생했습니다.'
        }), 500

@app.route('/api/reports/download/<filename>')
def download_report(filename):
    try:
        report_path = os.path.join('reports', filename)
        return send_file(
            report_path,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '리포트 다운로드 중 오류가 발생했습니다.'
        }), 404

@app.route('/api/reports/list')
def list_reports():
    try:
        reports_dir = 'reports'
        os.makedirs(reports_dir, exist_ok=True)
        reports = []
        
        for filename in os.listdir(reports_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(reports_dir, filename)
                with open(file_path, 'r') as f:
                    report_data = json.load(f)
                reports.append({
                    'filename': filename,
                    'timestamp': report_data['timestamp'],
                    'type': report_data['type'],
                    'period': report_data['period']
                })
        
        return jsonify({
            'success': True,
            'reports': sorted(reports, key=lambda x: x['timestamp'], reverse=True)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '리포트 목록을 가져오는 중 오류가 발생했습니다.'
        }), 500

@app.route('/api/processes')
def get_processes():
    return jsonify(process_monitor.get_process_list())

@app.route('/api/network/stats')
def get_network_stats():
    try:
        stats = network_monitor.get_network_stats()
        return jsonify({
            'status': 'success',
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/logs/search')
def search_logs():
    query = request.args.get('query', '')
    level = request.args.get('level', 'all')
    page = int(request.args.get('page', 1))
    return jsonify(log_analyzer.search_logs(query=query, level=level, page=page))

@app.route('/api/performance/score')
def get_performance_score():
    metrics = metrics_collector.get_all_metrics()
    score = performance_analyzer.calculate_performance_score(metrics)
    return jsonify({'score': score})

@app.route('/api/reports/delete/<filename>', methods=['DELETE'])
def delete_report(filename):
    try:
        # 파일 경로
        json_path = os.path.join('reports', f"{filename}.json")
        excel_path = os.path.join('reports', f"{filename}.xlsx")
        
        # 파일 존재 여부 확인 후 삭제
        files_deleted = 0
        if os.path.exists(json_path):
            os.remove(json_path)
            files_deleted += 1
        if os.path.exists(excel_path):
            os.remove(excel_path)
            files_deleted += 1
            
        if files_deleted > 0:
            return jsonify({
                'success': True,
                'message': '리포트가 삭제되었습니다.'
            })
        else:
            return jsonify({
                'success': False,
                'message': '삭제할 리포트를 찾을 수 없습니다.'
            }), 404
            
    except Exception as e:
        print(f"Delete error: {str(e)}")  # 디버깅을 위한 로그 추가
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '리포트 삭제 중 오류가 발생했습니다.'
        }), 500

@app.route('/api/network/ports')
def get_ports():
    try:
        # 일반적으로 모니터링할 포트 목록
        common_ports = [80, 443, 22, 21, 3306, 5432, 27017]
        results = []
        for port in common_ports:
            status = network_monitor.check_port_status(port)
            results.append(status)
        return jsonify({
            'status': 'success',
            'data': results
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/system/stats')
def get_system_stats():
    try:
        # CPU 정보
        cpu_percent = psutil.cpu_percent(interval=None)
        cpu_cores = psutil.cpu_count()

        # 메모리 정보
        memory = psutil.virtual_memory()
        memory_percent = memory.percent

        # 디스크 정보
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent

        # 운영체제 정보
        os_info = f"{platform.system()} {platform.release()}"

        # 실행 중인 프로세스 수
        running_processes = len(psutil.pids())

        # 업타임
        uptime = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")

        return jsonify({
            'status': 'success',
            'cpu_percent': cpu_percent,
            'cpu_cores': cpu_cores,
            'memory_percent': memory_percent,
            'total_memory': memory.total,
            'disk_percent': disk_percent,
            'os_info': os_info,
            'running_processes': running_processes,
            'uptime': uptime
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

@socketio.on('connect_ssh')
def handle_ssh_connection(data):
    try:
        hostname = data.get('hostname')
        username = data.get('username')
        key_path = data.get('key_path')
        
        if ssh_client.connect(hostname, username, key_path):
            emit('console_output', {'output': 'Successfully connected to AWS server\n'})
        else:
            emit('console_output', {'output': 'Failed to connect to AWS server\n'})
    except Exception as e:
        emit('console_output', {'output': f'Connection error: {str(e)}\n'})

@socketio.on('execute_command')
def handle_command(data):
    command = data['command']
    output = ssh_client.execute_command(command)
    emit('console_output', {'output': output})

@app.route('/aws-console')
def aws_console():
    return render_template('aws_console.html')

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5001) 