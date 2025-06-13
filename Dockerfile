FROM python:3.9.0-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install  -r requirements.txt --trusted-host mirrors.huaweicloud.com -i https://mirrors.huaweicloud.com/repository/pypi/simple

COPY . .

EXPOSE 8001

# 运行 uvicorn 服务器
CMD ["uvicorn", "kingbaseslot-exporter:app", "--host", "0.0.0.0", "--port", "8001"]