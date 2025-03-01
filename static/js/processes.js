document.addEventListener('DOMContentLoaded', function() {
    const processList = document.getElementById('processList');
    const processSearch = document.getElementById('processSearch');
    const refreshBtn = document.getElementById('refreshBtn');

    function loadProcesses() {
        fetch('/api/processes')
            .then(response => response.json())
            .then(processes => {
                const filteredProcesses = processes.filter(process => 
                    process.name.toLowerCase().includes(processSearch.value.toLowerCase())
                );
                
                processList.innerHTML = filteredProcesses.map(process => `
                    <tr>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${process.pid}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${process.name}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${process.cpu_percent.toFixed(1)}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${process.memory_percent.toFixed(1)}</td>
                        <td class="px-6 py-4 whitespace-nowrap">
                            <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                                실행 중
                            </span>
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            <button onclick="controlProcess(${process.pid}, 'stop')" 
                                    class="text-red-600 hover:text-red-900">중지</button>
                        </td>
                    </tr>
                `).join('');
            })
            .catch(error => console.error('Error:', error));
    }

    function controlProcess(pid, action) {
        fetch(`/api/processes/${pid}/${action}`, { method: 'POST' })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    loadProcesses();
                } else {
                    alert('프로세스 제어 실패');
                }
            })
            .catch(error => console.error('Error:', error));
    }

    refreshBtn.addEventListener('click', loadProcesses);
    processSearch.addEventListener('input', loadProcesses);
    
    // 초기 로드
    loadProcesses();
    // 5초마다 자동 새로고침
    setInterval(loadProcesses, 5000);
}); 