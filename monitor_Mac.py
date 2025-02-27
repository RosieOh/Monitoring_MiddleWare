import logging
import platform
import signal
import subprocess
import sys
from time import sleep

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitor.log'),
        logging.StreamHandler()
    ]
)

def signal_handler(signum, frame):
    logging.info("모니터링을 종료합니다.")
    sys.exit(0)

def is_process_running(process_name):
    try:
        # macOS에서 실행 중인 파이썬 프로세스 확인
        cmd = ['pgrep', '-f', process_name]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return bool(result.stdout.strip())
    except Exception as e:
        logging.error(f"프로세스 확인 중 오류 발생: {str(e)}")
        return False

def start_process(process_name):
    try:
        subprocess.Popen(['python3', process_name])
        logging.info(f"{process_name} 프로세스를 시작했습니다.")
        return True
    except Exception as e:
        logging.error(f"프로세스 시작 중 오류 발생: {str(e)}")
        return False

def check(process_name):
    try:
        if not is_process_running(process_name):
            logging.warning(f"{process_name} 프로세스가 실행되지 않고 있습니다. 재시작합니다.")
            start_process(process_name)
        else:
            logging.info(f"{process_name} 프로세스가 실행 중입니다.")
    
    except Exception as e:
        logging.error(f"예상치 못한 오류 발생: {str(e)}")

if __name__ == '__main__':
    # Ctrl+C 시그널 핸들러 등록
    signal.signal(signal.SIGINT, signal_handler)
    
    # 모니터링할 프로세스 이름 (커맨드라인 인자로 받거나 기본값 사용)
    process_name = sys.argv[1] if len(sys.argv) > 1 else "test_script.py"
    
    logging.info(f"모니터링을 시작합니다. 대상 프로세스: {process_name}")
    
    # 처음 실행
    if not is_process_running(process_name):
        start_process(process_name)
    
    # 무한 루프로 실행
    while True:
        sleep(5)
        check(process_name)