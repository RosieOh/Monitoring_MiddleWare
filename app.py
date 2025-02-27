from pathlib import Path

from flask import Flask, jsonify, render_template, send_file
from flask_cors import CORS

from metrics_collector import MetricsCollector

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET"],
        "allow_headers": ["Content-Type"]
    }
})

metrics_collector = MetricsCollector()

# 기본 루트 대시보드 페이지 추가
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

# Node_Exporter 수집 기전을 응용한 데이터 수집 방식 추가
@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    try:
        return jsonify(metrics_collector.get_all_metrics()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 엑셀 내보내기 기능 추가
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

# 메인 실행 함수
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True) 