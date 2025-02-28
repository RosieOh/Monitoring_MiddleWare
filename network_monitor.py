import psutil
import speedtest
from scapy.all import *


class NetworkMonitor:
    def __init__(self):
        self.speed_test = speedtest.Speedtest()
        
    def get_network_stats(self):
        stats = psutil.net_io_counters()
        return {
            'bytes_sent': stats.bytes_sent,
            'bytes_recv': stats.bytes_recv,
            'packets_sent': stats.packets_sent,
            'packets_recv': stats.packets_recv
        }

    def check_port_status(self, host, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except:
            return False 