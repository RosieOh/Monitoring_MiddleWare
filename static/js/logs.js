document.addEventListener('DOMContentLoaded', function() {
    const logList = document.getElementById('logList');
    const logSearch = document.getElementById('logSearch');
    const logLevel = document.getElementById('logLevel');
    const startDate = document.getElementById('startDate');
    const endDate = document.getElementById('endDate');
    const applyFilter = document.getElementById('applyFilter');
    
    let currentPage = 1;
    const logsPerPage = 50;

    function loadLogs() {
        const params = new URLSearchParams({
            search: logSearch.value,
            level: logLevel.value,
            start: startDate.value,
            end: endDate.value,
            page: currentPage,
            per_page: logsPerPage
        });

        fetch(`/api/logs?${params}`)
            .then(response => response.json())
            .then(data => {
                logList.innerHTML = data.logs.map(log => `
                    <tr>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            ${new Date(log.timestamp).toLocaleString()}
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap">
                            <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                                ${getLevelClass(log.level)}">
                                ${log.level}
                            </span>
                        </td>
                        <td class="px-6 py-4 text-sm text-gray-900">${log.message}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${log.source}</td>
                    </tr>
                `).join('');

                document.getElementById('totalLogs').textContent = data.total;
                updatePagination(data.total);
            })
            .catch(error => console.error('Error:', error));
    }

    function getLevelClass(level) {
        const classes = {
            'ERROR': 'bg-red-100 text-red-800',
            'WARNING': 'bg-yellow-100 text-yellow-800',
            'INFO': 'bg-blue-100 text-blue-800'
        };
        return classes[level] || 'bg-gray-100 text-gray-800';
    }

    function updatePagination(total) {
        const totalPages = Math.ceil(total / logsPerPage);
        const pagination = document.getElementById('pagination');
        
        let paginationHtml = '';
        
        if (currentPage > 1) {
            paginationHtml += `
                <button onclick="changePage(${currentPage - 1})" 
                        class="px-3 py-1 rounded-md bg-gray-200 hover:bg-gray-300">
                    이전
                </button>
            `;
        }

        for (let i = Math.max(1, currentPage - 2); i <= Math.min(totalPages, currentPage + 2); i++) {
            paginationHtml += `
                <button onclick="changePage(${i})" 
                        class="px-3 py-1 rounded-md ${i === currentPage ? 'bg-blue-600 text-white' : 'bg-gray-200 hover:bg-gray-300'}">
                    ${i}
                </button>
            `;
        }

        if (currentPage < totalPages) {
            paginationHtml += `
                <button onclick="changePage(${currentPage + 1})" 
                        class="px-3 py-1 rounded-md bg-gray-200 hover:bg-gray-300">
                    다음
                </button>
            `;
        }

        pagination.innerHTML = paginationHtml;
    }

    window.changePage = function(page) {
        currentPage = page;
        loadLogs();
    };

    logSearch.addEventListener('input', () => {
        currentPage = 1;
        loadLogs();
    });

    logLevel.addEventListener('change', () => {
        currentPage = 1;
        loadLogs();
    });

    applyFilter.addEventListener('click', () => {
        currentPage = 1;
        loadLogs();
    });

    // 초기 로드
    loadLogs();
}); 