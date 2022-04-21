FROM python:3.9-slim
WORKDIR /usr/src/app
COPY requirements.txt ./
COPY gunicorn.sh ./
RUN pip install --no-cache-dir -r requirements.txt
COPY ./ ./
ENTRYPOINT ["sh", "./gunicorn.sh"]
