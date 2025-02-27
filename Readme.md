# 📌 Flask 기반 시스템 모니터링 API & 프로세스 자동 실행 스크립트

## 📂 프로젝트 개요
이 프로젝트는 시스템 리소스를 모니터링하는 **Flask 기반 API**와 특정 프로세스를 자동으로 실행하는 **Python 스크립트**로 구성됩니다. 💡

1. `Metrics.py` - **CPU, 메모리, 디스크 I/O 정보를 제공하는 API 서버**
2. `monitor.py` - **특정 프로세스가 실행되지 않으면 자동으로 실행하는 스크립트**

---

## 🚀 1. Metrics.py - 시스템 모니터링 API

### 🛠 주요 기능
- 1분 평균 **CPU 사용률** 계산
- **메모리 사용량** (총 용량, 사용량, 사용률) 제공
- 최근 5분간의 **디스크 IOPS(초당 입출력 작업 수)** 계산
- Flask API로 **JSON 데이터 반환**

### 🏗 사용 기술
- **Flask** - API 서버 구축
- **psutil** - 시스템 리소스 모니터링
- **CORS** - Cross-Origin 요청 허용

### 📜 코드 설명
- **CPU 평균 사용률 계산**: 1분 동안 샘플을 저장하여 평균값 반환
- **메모리 사용량 계산**: `psutil.virtual_memory()`로 총량, 사용량, 사용률 가져오기
- **디스크 IOPS 계산**: `psutil.disk_io_counters()`를 사용하여 읽기/쓰기 작업 수 측정
- **Flask API** (`/api/metrics`)로 JSON 데이터 반환

### 🔧 실행 방법
```bash
pip install flask flask_cors psutil
python Metrics.py
```
- 실행 후 `http://localhost:5005/api/metrics` 로 접속하면 시스템 모니터링 데이터를 JSON 형태로 확인 가능 ✅

---

## 🔄 2. monitor.py - 프로세스 자동 실행 스크립트

### 🛠 주요 기능
- 특정 프로세스 (`Metrics.py`)가 실행 중인지 확인
- 실행되지 않았다면 자동으로 실행
- 5초마다 프로세스를 체크하여 누락 방지

### 📜 코드 설명
- `ps -aux | grep /home/user/test/Metrics.py` 명령어로 실행 여부 확인
- 실행되지 않았다면 `python3 /home/user/test/Metrics.py &` 명령어 실행
- `sleep(5)`를 사용하여 5초 간격으로 체크

### 🔧 실행 방법
```bash
python ProcessChecker.py
```
- `Metrics.py`가 실행 중인지 5초마다 확인하고, 실행되지 않았다면 자동 실행됨 ✅

---

## 🎯 활용 예시
✅ **서버 모니터링 시스템** 구축
✅ **자동 복구 기능** - 서비스가 중단되면 자동으로 재시작
✅ **IoT, 클라우드 모니터링** 등 다양한 환경에서 활용 가능

---

