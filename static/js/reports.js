// CSRF 토큰을 가져오는 함수
function getCsrfToken() {
    return document.querySelector('input[name="csrf_token"]').value;
}

// 리포트 생성 함수
function generateReport() {
    console.log('Generating Report...'); // 함수 실행 확인
    
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    const reportType = document.getElementById('reportType').value;

    console.log('Input values:', { startDate, endDate, reportType }); // 입력값 확인

    if (!startDate || !endDate) {
        alert('시작 날짜와 종료 날짜를 선택해주세요.');
        return;
    }

    fetch('/api/reports/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
            startDate: startDate,
            endDate: endDate,
            type: reportType
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Response data:', data); // 응답 데이터 확인
        if (data.status === 'success') {
            alert('리포트가 생성되었습니다.');
            loadReports(); // 목록 새로고침
        } else {
            alert('리포트 생성 실패: ' + (data.message || '알 수 없는 오류가 발생했습니다.'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('리포트 생성 중 오류가 발생했습니다.');
    });
}

// 리포트 다운로드 함수
function downloadReport(reportId, format) {
    fetch(`/api/reports/download/${reportId}/${format}`, {
        headers: {
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `report_${reportId}.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();
    })
    .catch(error => {
        console.error('Error:', error);
        alert('리포트 다운로드 중 오류가 발생했습니다.');
    });
}

// 리포트 목록 로드 함수
function loadReports() {
    fetch('/api/reports/list', {
        headers: {
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log('Server response:', data); // 디버깅용
        const reportList = document.getElementById('reportList');
        const reports = data.reports || []; // data.reports 배열 사용
        
        if (reports.length > 0) {
            reportList.innerHTML = reports.map(report => `
                <div class="flex justify-between items-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                    <div>
                        <h3 class="font-medium text-gray-900">${report.title}</h3>
                        <p class="text-sm text-gray-500">${report.date}</p>
                    </div>
                    <div class="flex space-x-2">
                        <button onclick="downloadReport('${report.id}', 'csv')" 
                                class="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors">
                            CSV
                        </button>
                        <button onclick="downloadReport('${report.id}', 'excel')" 
                                class="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700 transition-colors">
                            Excel
                        </button>
                        <button onclick="deleteReport('${report.id}')" 
                                class="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700 transition-colors">
                            삭제
                        </button>
                    </div>
                </div>
            `).join('');
        } else {
            reportList.innerHTML = '<p class="text-center text-gray-500 py-4">생성된 리포트가 없습니다.</p>';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('reportList').innerHTML = 
            '<p class="text-center text-red-500 py-4">리포트 목록을 불러오는 중 오류가 발생했습니다.</p>';
    });
}

// 이벤트 리스너 등록
document.addEventListener('DOMContentLoaded', function() {
    const generateReportBtn = document.getElementById('generateReportBtn');
    if (generateReportBtn) {
        generateReportBtn.addEventListener('click', generateReport);
    }
    
    // 초기 리포트 목록 로드
    loadReports();
});

function deleteReport(filename) {
    if (confirm('이 리포트를 삭제하시겠습니까?')) {
        fetch(`/api/reports/delete/${filename}`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCsrfToken()
            }
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