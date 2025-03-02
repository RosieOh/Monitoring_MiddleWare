# 📌 Flask 기반 시스템 모니터링 대시보드

## 📂 프로젝트 개요
이 프로젝트는 시스템 리소스를 모니터링하고 관리하는 웹 기반 대시보드입니다. Flask 기반의 백엔드 API와 반응형 웹 프론트엔드로 구성되어 있습니다. 💡

### 주요 기능
- 실시간 시스템 리소스 모니터링 (CPU, 메모리, 디스크)
- 프로세스 모니터링 및 관리
- 네트워크 트래픽 모니터링
- 시스템 로그 분석
- 성능 분석 리포트 생성
- AWS 인스턴스 연동 및 관리

## 🔨 기술 스택
- **Backend**: Flask, Python 3.9
- **Frontend**: HTML5, TailwindCSS, JavaScript
- **Monitoring**: psutil, paramiko
- **Database**: SQLite (향후 MySQL/PostgreSQL 지원 예정)
- **Deployment**: Docker, Docker Compose

## 🚀 시작하기

### 로컬 개발 환경 설정

1. **가상환경 설정**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

2. **의존성 설치**
```bash
pip install -r requirements.txt
```

3. **애플리케이션 실행**
```bash
python app.py
```

### 🐳 Docker를 사용한 실행

1. **Docker 컨테이너 빌드 및 실행**
```bash
docker-compose up -d --build
```

2. **로그 확인**
```bash
docker-compose logs -f
```

## 📚 주요 컴포넌트

### 1. 대시보드 (/monitor)
- 시스템 리소스 실시간 모니터링
- 그래프 기반 데이터 시각화
- 알림 설정 및 관리

### 2. 프로세스 관리 (/processes)
- 실행 중인 프로세스 목록
- 프로세스 상태 모니터링
- 프로세스 시작/중지/재시작

### 3. 네트워크 모니터링 (/network)
- 네트워크 트래픽 분석
- 포트 상태 모니터링
- 연결 상태 확인

### 4. 로그 분석 (/logs)
- 시스템 로그 수집
- 로그 필터링 및 검색
- 이상 징후 감지

### 5. 리포트 생성 (/reports)
- 시스템 성능 리포트 생성
- CSV/Excel 형식 지원
- 커스텀 리포트 템플릿

## 🆕 최근 업데이트 (2024.03)

### 새로운 기능
- 리포트 생성 및 관리 시스템 추가
- Excel/CSV 형식의 리포트 다운로드 지원
- Docker 기반 배포 환경 구성
- AWS 통합 지원

### 개선사항
- UI/UX 개선 (TailwindCSS 적용)
- 실시간 데이터 업데이트 최적화
- 보안 강화 (CSRF 보호 추가)
- 에러 처리 및 로깅 개선

## 🌐 AWS 배포 가이드

### 사전 준비
1. AWS EC2 인스턴스 생성
2. 보안 그룹 설정 (포트 5001 개방)
3. Docker 및 Docker Compose 설치

### 배포 단계
```bash
# 코드 복제
git clone <repository-url>
cd <project-directory>

# 환경 설정
cp .env.example .env
# .env 파일 수정

# 배포
docker-compose up -d
```

## 🔧 설정 및 커스터마이징

### 환경 변수
- `FLASK_ENV`: 실행 환경 (development/production)
- `SECRET_KEY`: 애플리케이션 보안 키
- `PORT`: 서버 포트 (기본: 5001)

### 설정 파일
- `config.py`: 기본 설정
- `docker-compose.yml`: Docker 설정
- `requirements.txt`: Python 패키지 목록

## ⚠️ 주의사항
- 프로덕션 환경에서는 반드시 보안 설정을 확인하세요
- 정기적인 백업을 설정하세요
- 민감한 정보는 환경 변수로 관리하세요
- 리소스 사용량을 모니터링하세요

## 📝 라이선스
이 프로젝트는 MIT 라이선스를 따릅니다.

## 🤝 기여하기
버그 리포트, 기능 제안, 풀 리퀘스트를 환영합니다!

## 📞 지원
문제가 발생하면 이슈를 생성하거나 프로젝트 관리자에게 연락하세요.