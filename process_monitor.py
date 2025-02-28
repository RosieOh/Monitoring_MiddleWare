from datetime import datetime

import psutil


class ProcessMonitor:
    def __init__(self):
        self.watched_processes = {}
        
    def get_process_list(self):
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return processes

    def control_process(self, pid, action):
        try:
            process = psutil.Process(pid)
            if action == 'stop':
                process.terminate()
            elif action == 'restart':
                process.restart()
            return True
        except psutil.NoSuchProcess:
            return False 