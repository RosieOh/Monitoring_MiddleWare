import numpy as np
from sklearn.preprocessing import StandardScaler


class PerformanceAnalyzer:
    def __init__(self):
        self.scaler = StandardScaler()
        self.metrics_history = []
        
    def calculate_performance_score(self, metrics):
        weights = {
            'cpu': 0.4,
            'memory': 0.3,
            'disk': 0.2,
            'network': 0.1
        }
        
        score = sum(
            metrics[key] * weights[key]
            for key in weights
        )
        return score

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