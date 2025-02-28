document.addEventListener('DOMContentLoaded', function() {
    const generateReportBtn = document.getElementById('generateReportBtn');
    const dateFilter = document.getElementById('dateFilter');
    const reportType = document.getElementById('reportType');
    const reportsList = document.getElementById('reportsList');

    // 오늘 날짜를 기본값으로 설정
    dateFilter.valueAsDate = new Date();

    // 리포트 생성 버튼 클릭 이벤트
    generateReportBtn.addEventListener('click', async () => {
        const date = dateFilter.value;
        const type = reportType.value;
        
        try {
            const response = await fetch('/api/generate-report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    date: date,
                    type: type
                })
            });

            if (!response.ok) {
                throw new Error('리포트 생성 실패');
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `system_report_${type}_${date}.csv`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();

            // 리포트 목록 업데이트
            loadReports();
        } catch (error) {
            console.error('Error:', error);
            alert('리포트 생성에 실패했습니다.');
        }
    });

    // 리포트 목록 로드 함수
    async function loadReports() {
        try {
            const response = await fetch('/api/reports');
            if (!response.ok) {
                throw new Error('리포트 목록 로드 실패');
            }

            const reports = await response.json();
            displayReports(reports);
        } catch (error) {
            console.error('Error:', error);
            reportsList.innerHTML = '<p class="error">리포트 목록을 불러올 수 없습니다.</p>';
        }
    }

    // 리포트 목록 표시 함수
    function displayReports(reports) {
        if (reports.length === 0) {
            reportsList.innerHTML = '<p>생성된 리포트가 없습니다.</p>';
            return;
        }

        const html = reports.map(report => `
            <div class="report-item">
                <div class="report-info">
                    <h3>${report.type} 리포트</h3>
                    <p>생성일: ${report.created_at}</p>
                </div>
                <div class="report-actions">
                    <button onclick="downloadReport('${report.id}')" class="download-btn">다운로드</button>
                </div>
            </div>
        `).join('');

        reportsList.innerHTML = html;
    }

    // 초기 리포트 목록 로드
    loadReports();
});

// 리포트 다운로드 함수
async function downloadReport(reportId) {
    try {
        const response = await fetch(`/api/reports/${reportId}/download`);
        if (!response.ok) {
            throw new Error('리포트 다운로드 실패');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `report_${reportId}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();
    } catch (error) {
        console.error('Error:', error);
        alert('리포트 다운로드에 실패했습니다.');
    }
} 