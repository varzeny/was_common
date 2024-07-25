FROM python:3.10-slim

# 컨테이너의 작업 디렉토리를 설정 
WORKDIR /was_common

# requirements.txt를 컨테이너의 작업 디렉토리로 복사
COPY requirements.txt requirements.txt

# 종속성 설치
RUN pip install -r requirements.txt

# 코드 파일 전체를 컨테이너의 작업 디렉토리로 복사
# COPY . .
# run 시 mount 할 것

# 애플리케이션 시작 명령어
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8443"]
