document.addEventListener('DOMContentLoaded', function() {
    const reportList = document.getElementById('reportList');
    const generateReportBtn = document.getElementById('generateReport');
    const startDateInput = document.getElementById('startDate');
    const endDateInput = document.getElementById('endDate');
    const reportTypeSelect = document.getElementById('reportType');

    // 날짜 입력 필드 초기값 설정
    const now = new Date();
    const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
    startDateInput.value = sevenDaysAgo.toISOString().split('T')[0];
    endDateInput.value = now.toISOString().split('T')[0];

    function loadReports() {
        fetch('/api/reports/list')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    reportList.innerHTML = data.reports.map(report => {
                        const baseFilename = report.filename.split('.')[0];
                        return `
                            <div class="bg-white p-6 rounded-lg shadow mb-4">
                                <div class="flex justify-between items-center">
                                    <div>
                                        <h3 class="text-lg font-medium text-gray-900">
                                            ${report.type} 리포트
                                        </h3>
                                        <p class="text-sm text-gray-500">
                                            생성일: ${new Date(report.timestamp).toLocaleString()}
                                        </p>
                                        <p class="text-sm text-gray-500">
                                            기간: ${new Date(report.period.start).toLocaleDateString()} - 
                                                  ${new Date(report.period.end).toLocaleDateString()}
                                        </p>
                                    </div>
                                    <div class="flex space-x-2">
                                        <a href="/api/reports/download/${baseFilename}.json" 
                                           class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                                            JSON
                                        </a>
                                        <a href="/api/reports/download/${baseFilename}.xlsx" 
                                           class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
                                            Excel
                                        </a>
                                        <button onclick="deleteReport('${baseFilename}')"
                                                class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors">
                                            삭제
                                        </button>
                                    </div>
                                </div>
                            </div>
                        `;
                    }).join('');
                } else {
                    reportList.innerHTML = '<p class="text-gray-500">리포트가 없습니다.</p>';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                reportList.innerHTML = '<p class="text-red-500">리포트 목록을 불러오는데 실패했습니다.</p>';
            });
    }

    generateReportBtn.addEventListener('click', function() {
        // 버튼 비활성화 및 로딩 상태 표시
        this.disabled = true;
        const originalText = this.textContent;
        this.textContent = '생성 중...';

        const data = {
            start_date: startDateInput.value,
            end_date: endDateInput.value,
            type: reportTypeSelect.value
        };

        fetch('/api/reports/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                alert('리포트가 생성되었습니다.');
                loadReports();  // 리포트 목록 새로고침
            } else {
                alert('리포트 생성 실패: ' + (result.message || '알 수 없는 오류가 발생했습니다.'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('리포트 생성 중 오류가 발생했습니다.');
        })
        .finally(() => {
            // 버튼 상태 복원
            this.disabled = false;
            this.textContent = originalText;
        });
    });

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

function deleteReport(filename) {
    if (confirm('이 리포트를 삭제하시겠습니까?')) {
        fetch(`/api/reports/delete/${filename}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                alert('리포트가 삭제되었습니다.');
                loadReports();  // 리포트 목록 새로고침
            } else {
                alert('리포트 삭제 실패: ' + (result.message || '알 수 없는 오류가 발생했습니다.'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('리포트 삭제 중 오류가 발생했습니다.');
        });
    }
} 