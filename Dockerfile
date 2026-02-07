FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 安装系统依赖（增加 libmariadb-dev 以确保 pymysql 稳定）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libmariadb-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

COPY . .

# 暴露 Streamlit 默认端口
EXPOSE 8501
EXPOSE 8000

# CMD 虽然会被 Compose 覆盖，但保留一个默认值是好的
CMD ["streamlit", "run", "streamlit_app.py"]