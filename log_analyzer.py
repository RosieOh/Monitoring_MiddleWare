import re
from datetime import datetime

from elasticsearch import Elasticsearch


class LogAnalyzer:
    def __init__(self):
        self.es = Elasticsearch()
        self.log_patterns = {
            'error': r'ERROR|CRITICAL|FATAL',
            'warning': r'WARNING|WARN',
            'info': r'INFO'
        }
        
    def parse_log_file(self, file_path):
        logs = []
        with open(file_path, 'r') as f:
            for line in f:
                parsed = self.parse_log_line(line)
                if parsed:
                    logs.append(parsed)
        return logs

    def search_logs(self, query, start_time=None, end_time=None):
        # Elasticsearch 검색 로직
        search_body = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"message": query}}
                    ]
                }
            }
        }
        return self.es.search(index="logs", body=search_body) 