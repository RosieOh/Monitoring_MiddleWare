import logging
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file
from flask_cors import CORS

from metrics_collector import MetricsCollector

app = Flask(__name__)
CORS(app)

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

metrics_collector = MetricsCollector()

@app.route('/')
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

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

@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    try:
        if not request.is_json:
            logger.error("Request does not contain JSON data")
            return jsonify({'error': 'Invalid request format'}), 400

        data = request.json
        logger.debug(f"Received report generation request with data: {data}")

        report_date = data.get('date')
        report_type = data.get('type')

        if not report_date or not report_type:
            logger.error("Missing required parameters")
            return jsonify({'error': 'Missing date or type parameter'}), 400

        logger.info(f"Generating {report_type} report for date {report_date}")
        file_path = metrics_collector.generate_report(report_date, report_type)
        
        if file_path:
            logger.info(f"Report generated successfully at {file_path}")
            return send_file(
                file_path,
                mimetype='text/csv',
                as_attachment=True,
                download_name=f"system_report_{report_type}_{report_date}.csv"
            )
        
        logger.error("No data available for report generation")
        return jsonify({'error': 'No data available'}), 404

    except Exception as e:
        logger.exception("Error during report generation")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports', methods=['GET'])
def get_reports():
    try:
        reports = metrics_collector.get_report_list()
        return jsonify(reports)
    except Exception as e:
        logger.exception("Error getting report list")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/<report_id>/download', methods=['GET'])
def download_report(report_id):
    try:
        file_path = metrics_collector.get_report_file(report_id)
        if file_path:
            return send_file(
                file_path,
                mimetype='text/csv',
                as_attachment=True,
                download_name=f"{report_id}.csv"
            )
        return jsonify({'error': 'Report not found'}), 404
    except Exception as e:
        logger.exception("Error downloading report")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True) 