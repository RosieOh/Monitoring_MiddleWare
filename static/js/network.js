document.addEventListener('DOMContentLoaded', function() {
    // 차트 컨텍스트 가져오기
    const networkTrafficCtx = document.getElementById('networkTrafficChart').getContext('2d');
    
    // 네트워크 트래픽 차트 설정
    const networkTrafficChart = new Chart(networkTrafficCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: '수신 (KB/s)',
                    borderColor: 'rgb(59, 130, 246)',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    data: [],
                    fill: true,
                    tension: 0.4
                },
                {
                    label: '송신 (KB/s)',
                    borderColor: 'rgb(16, 185, 129)',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    data: [],
                    fill: true,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: '전송량 (KB/s)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: '시간'
                    }
                }
            },
            animation: {
                duration: 750
            }
        }
    });

    // 네트워크 상태 업데이트 함수
    function updateNetworkStats() {
        fetch('/api/network/stats')
            .then(response => response.json())
            .then(data => {
                const now = new Date().toLocaleTimeString();
                
                // 트래픽 차트 업데이트
                networkTrafficChart.data.labels.push(now);
                networkTrafficChart.data.datasets[0].data.push(data.bytes_recv_per_sec / 1024); // KB로 변환
                networkTrafficChart.data.datasets[1].data.push(data.bytes_sent_per_sec / 1024);
                
                // 최대 30개 데이터 포인트 유지
                if (networkTrafficChart.data.labels.length > 30) {
                    networkTrafficChart.data.labels.shift();
                    networkTrafficChart.data.datasets[0].data.shift();
                    networkTrafficChart.data.datasets[1].data.shift();
                }
                
                networkTrafficChart.update();

                // 속도 표시 업데이트
                document.getElementById('downloadSpeed').textContent = 
                    `${(data.bytes_recv_per_sec / 1024).toFixed(2)} KB/s`;
                document.getElementById('uploadSpeed').textContent = 
                    `${(data.bytes_sent_per_sec / 1024).toFixed(2)} KB/s`;
            })
            .catch(error => console.error('Error:', error));
    }

    document.getElementById('runSpeedTest').addEventListener('click', function() {
        this.disabled = true;
        this.textContent = '테스트 중...';

        fetch('/api/network/speedtest')
            .then(response => response.json())
            .then(data => {
                document.getElementById('downloadSpeed').textContent = 
                    `${data.download.toFixed(2)} Mbps`;
                document.getElementById('uploadSpeed').textContent = 
                    `${data.upload.toFixed(2)} Mbps`;
                document.getElementById('pingLatency').textContent = 
                    `${data.ping.toFixed(1)} ms`;
            })
            .catch(error => console.error('Error:', error))
            .finally(() => {
                this.disabled = false;
                this.textContent = '속도 테스트 실행';
            });
    });

    // 포트 상태 확인 부분 수정
    function updatePortStatus() {
        fetch('/api/network/ports')
            .then(response => response.json())
            .then(result => {
                if (result.status === 'success') {
                    const portsList = document.getElementById('portsList');
                    if (portsList) {
                        portsList.innerHTML = result.data.map(port => `
                            <div class="flex items-center justify-between p-2">
                                <span class="text-sm text-gray-600">포트 ${port.port}</span>
                                <span class="px-2 py-1 text-xs rounded-full ${
                                    port.status === 'open' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                                }">
                                    ${port.status}
                                </span>
                            </div>
                        `).join('');
                    }
                }
            })
            .catch(error => console.error('Error:', error));
    }

    // 초기 포트 상태 확인
    updatePortStatus();
    // 30초마다 포트 상태 업데이트
    setInterval(updatePortStatus, 30000);

    // 초기 로드
    updateNetworkStats();
    
    // 2초마다 업데이트
    setInterval(updateNetworkStats, 2000);
}); 