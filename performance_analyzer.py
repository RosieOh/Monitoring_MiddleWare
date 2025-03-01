import numpy as np
from sklearn.preprocessing import StandardScaler


class PerformanceAnalyzer:
    def __init__(self):
        self.weights = {
            'cpu': 0.3,
            'memory': 0.3,
            'disk': 0.2,
            'network': 0.2
        }
        self.scaler = StandardScaler()
        self.metrics_history = []
        
    def calculate_performance_score(self, metrics):
        try:
            scores = {
                'cpu': self._normalize_cpu(metrics['cpu']['percent']),
                'memory': self._normalize_memory(metrics['memory']['percent']),
                'disk': self._normalize_disk(metrics['disk']['percent']),
                'network': self._normalize_network(metrics['network'])
            }
            
            # 가중치를 적용한 최종 점수 계산
            score = sum(scores[key] * self.weights[key] for key in self.weights)
            return round(score, 2)
            
        except Exception as e:
            print(f"Error calculating performance score: {str(e)}")
            return 0

    def _normalize_cpu(self, cpu_percent):
        # CPU 사용률을 0-1 사이의 점수로 변환 (낮을수록 좋음)
        return max(0, 1 - (cpu_percent / 100))

    def _normalize_memory(self, memory_percent):
        # 메모리 사용률을 0-1 사이의 점수로 변환 (낮을수록 좋음)
        return max(0, 1 - (memory_percent / 100))

    def _normalize_disk(self, disk_percent):
        # 디스크 사용률을 0-1 사이의 점수로 변환 (낮을수록 좋음)
        return max(0, 1 - (disk_percent / 100))

    def _normalize_network(self, network_stats):
        try:
            # 네트워크 상태를 0-1 사이의 점수로 변환
            # 여기서는 간단히 연결 상태만 확인
            return 1.0 if network_stats.get('bytes_sent', 0) > 0 or network_stats.get('bytes_recv', 0) > 0 else 0.0
        except:
            return 0.0

    def analyze_bottlenecks(self, metrics):
        bottlenecks = []
        if metrics['cpu'] > 80:
            bottlenecks.append({
                'type': 'cpu',
                'severity': 'high',
                'recommendation': 'Consider scaling up CPU resources'
            })
        # ... other resource checks ...
        return bottlenecks 