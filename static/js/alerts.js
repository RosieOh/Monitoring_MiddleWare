document.addEventListener('DOMContentLoaded', function() {
    const alertSettingsForm = document.getElementById('alertSettingsForm');
    const testAlertButton = document.getElementById('testAlert');
    const alertHistory = document.getElementById('alertHistory');

    // 알림 설정 로드
    function loadAlertSettings() {
        fetch('/api/alerts/settings')
            .then(response => response.json())
            .then(settings => {
                alertSettingsForm.cpuThreshold.value = settings.cpu_threshold;
                alertSettingsForm.memoryThreshold.value = settings.memory_threshold;
                alertSettingsForm.diskThreshold.value = settings.disk_threshold;
                alertSettingsForm.emailAlerts.checked = settings.email_enabled;
                alertSettingsForm.slackAlerts.checked = settings.slack_enabled;
            })
            .catch(error => console.error('Error:', error));
    }

    // 알림 히스토리 로드
    function loadAlertHistory() {
        fetch('/api/alerts/history')
            .then(response => response.json())
            .then(alerts => {
                alertHistory.innerHTML = alerts.map(alert => `
                    <div class="flex items-center space-x-4 p-4 ${getAlertBgClass(alert.level)}">
                        <div class="flex-shrink-0">
                            ${getAlertIcon(alert.level)}
                        </div>
                        <div class="flex-1 min-w-0">
                            <p class="text-sm font-medium text-gray-900">
                                ${alert.message}
                            </p>
                            <p class="text-sm text-gray-500">
                                ${new Date(alert.timestamp).toLocaleString()}
                            </p>
                        </div>
                    </div>
                `).join('');
            })
            .catch(error => console.error('Error:', error));
    }

    function getAlertBgClass(level) {
        const classes = {
            'critical': 'bg-red-50',
            'warning': 'bg-yellow-50',
            'info': 'bg-blue-50'
        };
        return classes[level] || 'bg-gray-50';
    }

    function getAlertIcon(level) {
        const icons = {
            'critical': `
                <svg class="h-5 w-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                          d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
            `,
            'warning': `
                <svg class="h-5 w-5 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                          d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
                </svg>
            `,
            'info': `
                <svg class="h-5 w-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                          d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
            `
        };
        return icons[level] || icons['info'];
    }

    // 알림 설정 저장
    alertSettingsForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const settings = {
            cpu_threshold: parseFloat(this.cpuThreshold.value),
            memory_threshold: parseFloat(this.memoryThreshold.value),
            disk_threshold: parseFloat(this.diskThreshold.value),
            email_enabled: this.emailAlerts.checked,
            slack_enabled: this.slackAlerts.checked
        };

        fetch('/api/alerts/settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(settings)
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                alert('알림 설정이 저장되었습니다.');
            } else {
                alert('알림 설정 저장에 실패했습니다.');
            }
        })
        .catch(error => console.error('Error:', error));
    });

    // 테스트 알림 전송
    testAlertButton.addEventListener('click', function() {
        fetch('/api/alerts/test', { method: 'POST' })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    alert('테스트 알림이 전송되었습니다.');
                } else {
                    alert('테스트 알림 전송에 실패했습니다.');
                }
            })
            .catch(error => console.error('Error:', error));
    });

    // 초기 로드
    loadAlertSettings();
    loadAlertHistory();
    
    // 30초마다 알림 히스토리 업데이트
    setInterval(loadAlertHistory, 30000);
}); 