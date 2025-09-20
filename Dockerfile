# BE_FASTAPI/Dockerfile

# 1. 베이스 이미지: Python 3.11 공식 슬림 이미지 사용
FROM python:3.11-slim

# 2. 시간대 설정: 컨테이너의 시간대를 서울로 설정
ENV TZ=Asia/Seoul

# 3. 시스템 의존성 설치 (ffmpeg): 기존과 동일하게 ffmpeg 설치
#    - apt-get을 사용하는 이유는 베이스 이미지가 Debian 계열이기 때문입니다.
#    - 만약 FastAPI 프로젝트에서 ffmpeg를 사용하지 않는다면 이 부분은 삭제해도 됩니다.
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# 4. 작업 디렉토리 설정
WORKDIR /app

# 5. Python 의존성 설치 (Docker 캐싱 최적화)
#    - 소스 코드를 복사하기 전에 requirements.txt만 먼저 복사하여 설치합니다.
#    - 이렇게 하면 소스 코드가 변경되어도 의존성은 다시 설치하지 않아 빌드 속도가 빨라집니다.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. 소스 코드 복사
#    - 현재 디렉토리(Dockerfile이 있는 위치)의 모든 파일을 컨테이너의 /app 디렉토리로 복사합니다.
COPY . .

# 7. 포트 노출
#    - uvicorn의 기본 포트인 8000번을 노출합니다.
EXPOSE 8000

# 8. 애플리케이션 실행
#    - 컨테이너가 시작될 때 uvicorn 서버를 실행합니다.
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]