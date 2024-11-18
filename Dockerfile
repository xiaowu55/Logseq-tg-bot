FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置时区
ENV TZ=Asia/Shanghai

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制源代码
COPY src/telegram_logseq ./telegram_logseq

# 创建配置和日志目录
RUN mkdir -p /app/config /app/logs

# 设置环境变量
ENV PYTHONPATH=/app
ENV CONFIG_PATH=/app/config/config.ini

# 启动命令
CMD ["python", "-m", "telegram_logseq.main"] 