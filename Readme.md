# 📌 Flask 기반 시스템 모니터링 API & 프로세스 자동 실행 스크립트

## 📂 프로젝트 개요
이 프로젝트는 시스템 리소스를 모니터링하는 **Flask 기반 API**와 특정 프로세스를 자동으로 실행하는 **Python 스크립트**로 구성됩니다. 💡

1. `Metrics.py` - **CPU, 메모리, 디스크 I/O 정보를 제공하는 API 서버**
2. `monitor.py` - **특정 프로세스가 실행되지 않으면 자동으로 실행하는 스크립트**

## 🔨 환경 설정

### 가상환경 설정
1. **프로젝트 디렉토리 생성 및 이동**
```bash
mkdir metrics_project
cd metrics_project
```

2. **가상환경 생성**
```bash
python3 -m venv venv
```

3. **가상환경 활성화**
- macOS/Linux:
```bash
source venv/bin/activate
```
- Windows:
```bash
.\venv\Scripts\activate
```

4. **필요한 패키지 설치**
```bash
pip install flask flask-cors psutil
```

5. **의존성 패키지 목록 저장** (선택사항)
```bash
pip freeze > requirements.txt
```

### 가상환경 사용
- **가상환경 비활성화**
```bash
deactivate
```

- **다른 환경에서 패키지 설치** (requirements.txt 사용)
```bash
pip install -r requirements.txt
```

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
1. **가상환경 활성화**
```bash
source venv/bin/activate  # macOS/Linux
# 또는
.\venv\Scripts\activate  # Windows
```

2. **API 서버 실행**
```bash
python Metrics.py
```

3. **API 테스트**
- 브라우저에서 접속: `http://localhost:5001/api/metrics`
- 또는 curl 명령어 사용:
```bash
curl http://localhost:5001/api/metrics
```

### 📊 반환 데이터 예시
```json
{
    "cpu": 23.45,
    "memory": {
        "total_gb": 16.0,
        "used_gb": 12.34,
        "usage_percent": 77.12
    },
    "disk_io": {
        "read_iops": 1.23,
        "write_iops": 0.45
    },
    "datetime": "2024-02-20 15:30:45"
}
```

## 🔄 2. monitor.py - 프로세스 자동 실행 스크립트

### 🛠 주요 기능
- 특정 프로세스 (`Metrics.py`)가 실행 중인지 확인
- 실행되지 않았다면 자동으로 실행
- 5초마다 프로세스를 체크하여 누락 방지
- 로깅 기능 제공 (파일 및 콘솔 출력)
- 안전한 종료 처리 (Ctrl+C)

### 📜 코드 설명
- 프로세스 실행 여부 확인 (OS별 최적화)
- 자동 재시작 기능
- 로그 파일 생성 및 관리
- 시그널 핸들링

### 🔧 실행 방법
1. **새 터미널에서 가상환경 활성화**
```bash
source venv/bin/activate  # macOS/Linux
# 또는
.\venv\Scripts\activate  # Windows
```

2. **모니터링 스크립트 실행**
```bash
python monitor.py Metrics.py
```

3. **다른 프로세스 모니터링** (선택사항)
```bash
python monitor.py other_script.py
```

## 🎯 활용 예시
✅ **서버 모니터링 시스템** 구축
- 시스템 리소스 사용량 실시간 모니터링
- 성능 분석 및 병목 현상 파악
- 리소스 사용량 추이 분석

✅ **자동 복구 기능**
- 서비스 중단 시 자동 재시작
- 무중단 서비스 유지
- 시스템 안정성 향상

✅ **확장 가능한 모니터링**
- IoT 디바이스 모니터링
- 클라우드 서비스 모니터링
- 커스텀 메트릭 추가 가능

## ⚠️ 주의사항
- 가상환경을 사용하면 프로젝트별로 독립된 Python 환경을 유지할 수 있습니다.
- 새 터미널 창을 열 때마다 가상환경을 다시 활성화해야 합니다.
- 프로젝트 공유 시 `requirements.txt`를 함께 공유하면 다른 환경에서도 쉽게 설정할 수 있습니다.
- 포트 5001이 이미 사용 중인 경우, Metrics.py의 포트 번호를 변경해야 할 수 있습니다.

## 📝 라이선스
이 프로젝트는 MIT 라이선스 하에 공개되어 있습니다.

## 🤝 기여하기
버그 리포트, 기능 제안, 풀 리퀘스트 등 모든 기여를 환영합니다!