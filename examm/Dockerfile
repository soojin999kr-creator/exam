# 파이썬 3.9 슬림 버전을 기반 이미지로 사용합니다.
FROM python:3.9-slim

# 컨테이너 내부의 작업 디렉토리를 /app으로 설정합니다.
WORKDIR /app

# 현재 디렉토리의 requirements.txt 파일을 컨테이너 내부로 복사합니다.
COPY requirements.txt .

# 필요한 파이썬 라이브러리를 설치합니다.
RUN pip install --no-cache-dir -r requirements.txt

# 프로젝트의 모든 파일(main.py 등)을 컨테이너 내부로 복사합니다.
COPY . .

# Cloud Run이 사용하는 기본 포트 8080을 외부로 개방합니다.
EXPOSE 8080

# 컨테이너가 실행될 때 uvicorn 명령어로 FastAPI 서버를 구동합니다.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
