import re
import socket
import subprocess
import time
from datetime import datetime

import psutil
import requests


class NetworkMonitor:
    def __init__(self):
        self.last_net_io = psutil.net_io_counters()
        self.last_net_time = time.time()
        
    def get_network_stats(self):
        try:
            current_net_io = psutil.net_io_counters()
            current_time = time.time()
            
            time_elapsed = current_time - self.last_net_time
            
            if time_elapsed > 0:  # 0으로 나누기 방지
                # 초당 전송량 계산 (bytes/s)
                bytes_sent = (current_net_io.bytes_sent - self.last_net_io.bytes_sent) / time_elapsed
                bytes_recv = (current_net_io.bytes_recv - self.last_net_io.bytes_recv) / time_elapsed
            else:
                bytes_sent = 0
                bytes_recv = 0
            
            # 현재 값을 다음 계산을 위해 저장
            self.last_net_io = current_net_io
            self.last_net_time = current_time
            
            # 모든 네트워크 인터페이스의 통계 수집
            interfaces_io = psutil.net_io_counters(pernic=True)
            total_bytes_sent = sum(nic.bytes_sent for nic in interfaces_io.values())
            total_bytes_recv = sum(nic.bytes_recv for nic in interfaces_io.values())
            
            return {
                'bytes_sent_per_sec': max(0, round(bytes_sent, 2)),  # 음수 방지
                'bytes_recv_per_sec': max(0, round(bytes_recv, 2)),  # 음수 방지
                'total_bytes_sent': total_bytes_sent,
                'total_bytes_recv': total_bytes_recv,
            }
            
        except Exception as e:
            print(f"Error getting network stats: {str(e)}")
            return {
                'bytes_sent_per_sec': 0,
                'bytes_recv_per_sec': 0,
                'total_bytes_sent': 0,
                'total_bytes_recv': 0,
            }

    def get_active_connections(self):
        connections = []
        try:
            for conn in psutil.net_connections():
                if conn.status == 'ESTABLISHED':
                    try:
                        process = psutil.Process(conn.pid) if conn.pid else None
                        connections.append({
                            'local_address': f"{conn.laddr.ip}:{conn.laddr.port}",
                            'remote_address': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A",
                            'status': conn.status,
                            'pid': conn.pid,
                            'process_name': process.name() if process else "N/A"
                        })
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
        except Exception as e:
            print(f"Error getting connections: {str(e)}")
        return connections

    def get_network_interfaces(self):
        interfaces = []
        try:
            for name, addrs in psutil.net_if_addrs().items():
                interface = {
                    'name': name,
                    'addresses': [],
                    'status': 'up' if name in psutil.net_if_stats() and psutil.net_if_stats()[name].isup else 'down'
                }
                
                for addr in addrs:
                    if addr.family == socket.AF_INET:  # IPv4
                        interface['addresses'].append({
                            'ip': addr.address,
                            'netmask': addr.netmask,
                            'type': 'IPv4'
                        })
                    elif addr.family == socket.AF_INET6:  # IPv6
                        interface['addresses'].append({
                            'ip': addr.address,
                            'netmask': addr.netmask,
                            'type': 'IPv6'
                        })
                
                interfaces.append(interface)
        except Exception as e:
            print(f"Error getting interfaces: {str(e)}")
        return interfaces

    def check_port_status(self, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            return {
                'port': port,
                'status': 'open' if result == 0 else 'closed'
            }
        except Exception as e:
            return {
                'port': port,
                'status': 'error',
                'error': str(e)
            }

    def measure_latency(self, host="8.8.8.8", count=4):
        try:
            if subprocess.call(["ping", "-c", "1", host], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) != 0:
                return None

            ping_output = subprocess.check_output(
                ["ping", "-c", str(count), host],
                universal_newlines=True
            )
            
            if "avg" in ping_output:
                avg_line = ping_output.split('=')[-1].strip()
                avg_time = float(avg_line.split('/')[1])
                return avg_time
            return None
        except:
            return None

    def run_speed_test(self):
        try:
            url = "http://speedtest.ftp.otenet.gr/files/test100k.db"
            start_time = time.time()
            response = requests.get(url, timeout=10)
            end_time = time.time()
            
            if response.status_code == 200:
                download_size = len(response.content)
                download_time = end_time - start_time
                speed_bps = (download_size * 8) / download_time
                speed_mbps = speed_bps / (1024 * 1024)
                
                return {
                    'download': round(speed_mbps, 2),
                    'upload': round(speed_mbps / 2, 2),
                    'ping': self.measure_latency() or 0
                }
        except Exception as e:
            print(f"Speed test error: {str(e)}")
            
        return {
            'download': 0,
            'upload': 0,
            'ping': 0
        } 