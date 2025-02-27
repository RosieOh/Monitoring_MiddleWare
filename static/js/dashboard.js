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