import json
import logging
import os
import platform
import subprocess
from datetime import datetime
from functools import wraps
from io import BytesIO
from pathlib import Path

import pandas as pd
import paramiko
import psutil
from flask import (Flask, flash, jsonify, redirect, render_template, request,
                   send_file, session, url_for)
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from flask_wtf.csrf import CSRFProtect

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

# CSRF 보호 설정
csrf = CSRFProtect()
csrf.init_app(app)

# 시크릿 키 설정
app.config['SECRET_KEY'] = 'your-secret-key-here'  # 실제 운영에서는 환경 변수로 관리

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

# 기본 계정 설정
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "1234"

# 로그인 필요 데코레이터
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# 루트 경로 (로그인 페이지)
@app.route('/', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('monitor'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember')

        if username == DEFAULT_USERNAME and password == DEFAULT_PASSWORD:
            session['user_id'] = username
            if remember:
                session.permanent = True
            return redirect(url_for('monitor'))
        else:
            return render_template('login.html', error="아이디 또는 비밀번호가 잘못되었습니다.")

    return render_template('login.html')

# 모니터링 메인 페이지
@app.route('/monitor')
@login_required
def monitor():
    return render_template('dashboard.html')  # 기존 대시보드 템플릿 사용

# 로그아웃 라우트
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# 기존 대시보드 라우트는 모니터 페이지로 리다이렉트
@app.route('/dashboard')
@login_required
def dashboard():
    return redirect(url_for('monitor'))

@app.route('/console')
def console():
    return render_template('console.html')

@app.route('/processes')
def processes():
    return render_template('processes.html')

@app.route('/network')
@login_required
def network():
    return render_template('network.html')

@app.route('/logs')
def logs():
    return render_template('logs.html')

@app.route('/alerts')
def alerts():
    return render_template('alerts.html')

@app.route('/performance')
@login_required
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

# 리포트를 저장할 전역 변수 (실제 구현에서는 데이터베이스를 사용해야 함)
generated_reports = []

@app.route('/api/reports/generate', methods=['POST'])
@login_required
def generate_report():
    try:
        data = request.get_json()
        report_id = datetime.now().strftime('%Y%m%d%H%M%S')
        
        # 새 리포트 생성
        report_data = {
            'id': report_id,
            'title': f"{data['type'].capitalize()} Report",
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'type': data['type'],
            'startDate': data['startDate'],
            'endDate': data['endDate'],
            'data': {
                'cpu_usage': '45%',
                'memory_usage': '60%',
                'disk_usage': '55%'
            }
        }
        
        # 생성된 리포트를 리스트에 추가
        generated_reports.insert(0, report_data)  # 최신 리포트를 앞에 추가
        
        return jsonify({
            'status': 'success',
            'message': '리포트가 생성되었습니다.',
            'report': report_data
        })

    except Exception as e:
        print(f"Error generating report: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '리포트 생성 중 오류가 발생했습니다.'
        }), 500

@app.route('/api/reports/download/<report_id>/<format>')
@login_required
def download_report(report_id, format):
    try:
        # 리포트 ID로 해당 리포트 찾기
        report = next((r for r in generated_reports if r['id'] == report_id), None)
        
        if not report:
            return jsonify({
                'status': 'error',
                'message': '리포트를 찾을 수 없습니다.'
            }), 404

        # 리포트 데이터를 DataFrame으로 변환
        report_data = {
            'Report ID': report['id'],
            'Type': report['type'],
            'Start Date': report['startDate'],
            'End Date': report['endDate'],
            'Generated Date': report['date'],
            'CPU Usage': report['data']['cpu_usage'],
            'Memory Usage': report['data']['memory_usage'],
            'Disk Usage': report['data']['disk_usage']
        }
        
        df = pd.DataFrame([report_data])

        if format == 'excel':
            # Excel 형식으로 변환
            output = BytesIO()
            df.to_excel(output, index=False, engine='openpyxl')
            output.seek(0)
            
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'report_{report_id}.xlsx'
            )
            
        elif format == 'csv':
            # CSV 형식으로 변환
            output = BytesIO()
            df.to_csv(output, index=False, encoding='utf-8-sig')  # UTF-8 with BOM for Excel
            output.seek(0)
            
            return send_file(
                output,
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'report_{report_id}.csv'
            )
            
        else:
            return jsonify({
                'status': 'error',
                'message': '지원하지 않는 형식입니다.'
            }), 400

    except Exception as e:
        print(f"Error downloading report: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '리포트 다운로드 중 오류가 발생했습니다.'
        }), 500

@app.route('/api/reports/list')
@login_required
def list_reports():
    try:
        # 실제 생성된 리포트 목록 반환
        return jsonify({
            'status': 'success',
            'reports': generated_reports
        })
    except Exception as e:
        print(f"Error listing reports: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '리포트 목록을 불러오는 중 오류가 발생했습니다.'
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