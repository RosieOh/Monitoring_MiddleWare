document.addEventListener('DOMContentLoaded', function() {
    const performanceScore = document.getElementById('performanceScore');
    const scoreBreakdown = document.getElementById('scoreBreakdown');
    const bottlenecks = document.getElementById('bottlenecks');
    const optimizationRecommendations = document.getElementById('optimizationRecommendations');

    // 성능 트렌드 차트 초기화
    const performanceTrendChart = new Chart(
        document.getElementById('performanceTrendChart').getContext('2d'),
        {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: '성능 점수',
                    borderColor: 'rgb(59, 130, 246)',
                    data: []
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        }
    );

    function updatePerformanceScore() {
        fetch('/api/performance/score')
            .then(response => response.json())
            .then(data => {
                // 성능 점수 업데이트
                performanceScore.textContent = Math.round(data.score);

                // 점수 세부 내역 업데이트
                scoreBreakdown.innerHTML = `
                    <div class="flex items-center justify-between">
                        <span class="text-sm text-gray-600">CPU 성능</span>
                        <div class="w-2/3">
                            <div class="h-2 bg-gray-200 rounded">
                                <div class="h-2 bg-blue-600 rounded" 
                                     style="width: ${data.breakdown.cpu}%"></div>
                            </div>
                        </div>
                        <span class="text-sm text-gray-900">${data.breakdown.cpu}%</span>
                    </div>
                    <div class="flex items-center justify-between">
                        <span class="text-sm text-gray-600">메모리 성능</span>
                        <div class="w-2/3">
                            <div class="h-2 bg-gray-200 rounded">
                                <div class="h-2 bg-green-600 rounded" 
                                     style="width: ${data.breakdown.memory}%"></div>
                            </div>
                        </div>
                        <span class="text-sm text-gray-900">${data.breakdown.memory}%</span>
                    </div>
                    <div class="flex items-center justify-between">
                        <span class="text-sm text-gray-600">디스크 성능</span>
                        <div class="w-2/3">
                            <div class="h-2 bg-gray-200 rounded">
                                <div class="h-2 bg-yellow-600 rounded" 
                                     style="width: ${data.breakdown.disk}%"></div>
                            </div>
                        </div>
                        <span class="text-sm text-gray-900">${data.breakdown.disk}%</span>
                    </div>
                    <div class="flex items-center justify-between">
                        <span class="text-sm text-gray-600">네트워크 성능</span>
                        <div class="w-2/3">
                            <div class="h-2 bg-gray-200 rounded">
                                <div class="h-2 bg-purple-600 rounded" 
                                     style="width: ${data.breakdown.network}%"></div>
                            </div>
                        </div>
                        <span class="text-sm text-gray-900">${data.breakdown.network}%</span>
                    </div>
                `;

                // 성능 트렌드 차트 업데이트
                const timestamp = new Date().toLocaleTimeString();
                performanceTrendChart.data.labels.push(timestamp);
                performanceTrendChart.data.datasets[0].data.push(data.score);

                if (performanceTrendChart.data.labels.length > 20) {
                    performanceTrendChart.data.labels.shift();
                    performanceTrendChart.data.datasets[0].data.shift();
                }

                performanceTrendChart.update();
            })
            .catch(error => console.error('Error:', error));
    }

    function updateBottlenecks() {
        fetch('/api/performance/bottlenecks')
            .then(response => response.json())
            .then(data => {
                bottlenecks.innerHTML = data.map(bottleneck => `
                    <div class="flex items-center space-x-4 p-4 ${getBottleneckBgClass(bottleneck.severity)}">
                        <div class="flex-shrink-0">
                            ${getBottleneckIcon(bottleneck.severity)}
                        </div>
                        <div>
                            <p class="text-sm font-medium text-gray-900">${bottleneck.type} 병목 현상</p>
                            <p class="text-sm text-gray-500">${bottleneck.description}</p>
                        </div>
                    </div>
                `).join('');
            })
            .catch(error => console.error('Error:', error));
    }

    function updateOptimizationRecommendations() {
        fetch('/api/performance/recommendations')
            .then(response => response.json())
            .then(data => {
                optimizationRecommendations.innerHTML = data.map(recommendation => `
                    <div class="border-l-4 border-blue-500 pl-4">
                        <h3 class="text-lg font-medium text-gray-900">${recommendation.title}</h3>
                        <p class="mt-1 text-sm text-gray-600">${recommendation.description}</p>
                        <div class="mt-2">
                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium 
                                       ${getPriorityClass(recommendation.priority)}">
                                ${recommendation.priority} 우선순위
                            </span>
                        </div>
                    </div>
                `).join('');
            })
            .catch(error => console.error('Error:', error));
    }

    function getBottleneckBgClass(severity) {
        const classes = {
            'high': 'bg-red-50',
            'medium': 'bg-yellow-50',
            'low': 'bg-blue-50'
        };
        return classes[severity] || 'bg-gray-50';
    }

    function getBottleneckIcon(severity) {
        const icons = {
            'high': `
                <svg class="h-5 w-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                          d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
            `,
            'medium': `
                <svg class="h-5 w-5 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                          d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
                </svg>
            `,
            'low': `
                <svg class="h-5 w-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                          d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
            `
        };
        return icons[severity] || icons['low'];
    }

    function getPriorityClass(priority) {
        const classes = {
            '높음': 'bg-red-100 text-red-800',
            '중간': 'bg-yellow-100 text-yellow-800',
            '낮음': 'bg-blue-100 text-blue-800'
        };
        return classes[priority] || 'bg-gray-100 text-gray-800';
    }

    // 성능 리포트 생성
    document.getElementById('generateReport').addEventListener('click', function() {
        fetch('/api/performance/report', { method: 'POST' })
            .then(response => response.blob())
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `performance_report_${new Date().toISOString().slice(0,10)}.pdf`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                a.remove();
            })
            .catch(error => console.error('Error:', error));
    });

    // 초기 로드
    updatePerformanceScore();
    updateBottlenecks();
    updateOptimizationRecommendations();

    // 주기적 업데이트
    setInterval(updatePerformanceScore, 5000);
    setInterval(updateBottlenecks, 30000);
    setInterval(updateOptimizationRecommendations, 60000);
}); 