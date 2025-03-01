// 차트 설정
const maxDataPoints = 60;
const charts = {
    cpu: createChart('cpuChart', '사용률 (%)', 'rgba(255, 99, 132, 0.2)', 'rgba(255, 99, 132, 1)'),
    memory: createChart('memoryChart', '사용률 (%)', 'rgba(54, 162, 235, 0.2)', 'rgba(54, 162, 235, 1)'),
    diskRead: createChart('diskReadChart', 'IOPS', 'rgba(75, 192, 192, 0.2)', 'rgba(75, 192, 192, 1)'),
    diskWrite: createChart('diskWriteChart', 'IOPS', 'rgba(153, 102, 255, 0.2)', 'rgba(153, 102, 255, 1)')
};

function createChart(canvasId, label, backgroundColor, borderColor) {
    return new Chart(document.getElementById(canvasId), {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: label,
                data: [],
                backgroundColor: backgroundColor,
                borderColor: borderColor,
                borderWidth: 1,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function updateChart(chart, value, label) {
    const data = chart.data.datasets[0].data;
    const labels = chart.data.labels;
    
    data.push(value);
    labels.push(label);

    if (data.length > maxDataPoints) {
        data.shift();
        labels.shift();
    }

    chart.update();
}

function fetchMetrics() {
    fetch('/api/metrics')
        .then(response => response.json())
        .then(data => {
            // 값 업데이트
            document.getElementById('cpu-value').textContent = `${data.cpu}%`;
            document.getElementById('memory-value').textContent = `${data.memory.usage_percent}%`;
            document.getElementById('disk-read').textContent = `${data.disk_io.read_iops} IOPS`;
            document.getElementById('disk-write').textContent = `${data.disk_io.write_iops} IOPS`;

            // 차트 업데이트
            const time = data.datetime.split(' ')[1];
            updateChart(charts.cpu, data.cpu, time);
            updateChart(charts.memory, data.memory.usage_percent, time);
            updateChart(charts.diskRead, data.disk_io.read_iops, time);
            updateChart(charts.diskWrite, data.disk_io.write_iops, time);
        })
        .catch(error => {
            console.error('Error:', error);
            ['cpu-value', 'memory-value', 'disk-read', 'disk-write'].forEach(id => {
                document.getElementById(id).textContent = 'Error';
            });
        });
}

// 1초마다 메트릭 업데이트
setInterval(fetchMetrics, 1000);
fetchMetrics(); // 초기 로드 

// 엑셀 내보내기 기능
document.getElementById('exportButton').addEventListener('click', async () => {
    try {
        const response = await fetch('/api/export-csv');
        if (!response.ok) {
            throw new Error('Export failed');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `metrics_log_${new Date().toISOString().slice(0,19).replace(/[:]/g, '')}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();
    } catch (error) {
        console.error('Error exporting data:', error);
        alert('데이터 내보내기에 실패했습니다.');
    }
});

document.addEventListener('DOMContentLoaded', function() {
    // 차트 생성 함수
    function createCharts() {
        // 차트 컨텍스트 가져오기
        const cpuChartElement = document.getElementById('cpuChart');
        const memoryChartElement = document.getElementById('memoryChart');
        const diskChartElement = document.getElementById('diskChart');

        if (!cpuChartElement || !memoryChartElement || !diskChartElement) {
            console.error('차트 요소를 찾을 수 없습니다');
            return;
        }

        // CPU 차트
        const cpuChart = new Chart(cpuChartElement, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'CPU 사용량',
                    borderColor: 'rgb(59, 130, 246)',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    data: [],
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: '사용량 (%)'
                        }
                    }
                }
            }
        });

        // 메모리 차트
        const memoryChart = new Chart(memoryChartElement, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: '메모리 사용량',
                    borderColor: 'rgb(16, 185, 129)',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    data: [],
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: '사용량 (%)'
                        }
                    }
                }
            }
        });

        // 디스크 차트
        const diskChart = new Chart(diskChartElement, {
            type: 'doughnut',
            data: {
                labels: ['사용됨', '여유'],
                datasets: [{
                    data: [0, 100],
                    backgroundColor: [
                        'rgb(139, 92, 246)',
                        'rgb(229, 231, 235)'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });

        return { cpuChart, memoryChart, diskChart };
    }

    // 차트 생성
    const charts = createCharts();
    if (!charts) return;

    // 시스템 상태 업데이트 함수
    function updateSystemStats() {
        fetch('/api/system/stats')
            .then(response => response.json())
            .then(data => {
                const now = new Date().toLocaleTimeString();

                // CPU 차트 업데이트
                charts.cpuChart.data.labels.push(now);
                charts.cpuChart.data.datasets[0].data.push(data.cpu_percent);
                if (charts.cpuChart.data.labels.length > 10) {
                    charts.cpuChart.data.labels.shift();
                    charts.cpuChart.data.datasets[0].data.shift();
                }
                charts.cpuChart.update();

                // 메모리 차트 업데이트
                charts.memoryChart.data.labels.push(now);
                charts.memoryChart.data.datasets[0].data.push(data.memory_percent);
                if (charts.memoryChart.data.labels.length > 10) {
                    charts.memoryChart.data.labels.shift();
                    charts.memoryChart.data.datasets[0].data.shift();
                }
                charts.memoryChart.update();

                // 디스크 차트 업데이트
                charts.diskChart.data.datasets[0].data = [data.disk_percent, 100 - data.disk_percent];
                charts.diskChart.update();

                // 텍스트 업데이트
                updateTextElements(data);
            })
            .catch(error => console.error('Error:', error));
    }

    // 텍스트 요소 업데이트 함수
    function updateTextElements(data) {
        const elements = {
            'cpuUsage': `${data.cpu_percent.toFixed(1)}%`,
            'memoryUsage': `${data.memory_percent.toFixed(1)}%`,
            'diskUsage': `${data.disk_percent.toFixed(1)}%`,
            'osInfo': data.os_info,
            'cpuCores': data.cpu_cores,
            'totalMemory': `${(data.total_memory / 1024 / 1024 / 1024).toFixed(1)} GB`,
            'runningProcesses': data.running_processes,
            'uptime': data.uptime
        };

        for (const [id, value] of Object.entries(elements)) {
            const element = document.getElementById(id);
            if (element) element.textContent = value;
        }
    }

    // 초기 로드
    updateSystemStats();
    
    // 2초마다 업데이트
    setInterval(updateSystemStats, 2000);
}); 