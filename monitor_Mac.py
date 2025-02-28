import json
import logging
import platform
import signal
import subprocess
import sys
from pathlib import Path
from time import sleep


class MonitoringSystem:
    def __init__(self):
        self.setup_logging()
        self.load_config()
        self.processes = {}

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/monitor.log'),
                logging.StreamHandler()
            ]
        )

    def load_config(self):
        try:
            with open('config/monitoring_config.json', 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {
                'processes': ['Metrics.py'],
                'check_interval': 5
            }

    def start_process(self, process_name):
        try:
            process = subprocess.Popen(['python3', process_name])
            self.processes[process_name] = process
            logging.info(f"Started {process_name}")
        except Exception as e:
            logging.error(f"Error starting {process_name}: {e}")

    def check_processes(self):
        for process_name in self.config['processes']:
            if process_name not in self.processes or self.processes[process_name].poll() is not None:
                logging.warning(f"Restarting {process_name}")
                self.start_process(process_name)

    def run(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        
        while True:
            self.check_processes()
            sleep(self.config['check_interval'])

    def signal_handler(self, signum, frame):
        logging.info("Shutting down monitoring system...")
        for process in self.processes.values():
            process.terminate()
        sys.exit(0)

if __name__ == '__main__':
    monitor = MonitoringSystem()
    monitor.run()