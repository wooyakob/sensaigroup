FROM amd64/python:3.11-slim-bookworm

WORKDIR /app

ADD . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["sh", "-c", "gunicorn --worker-tmp-dir /dev/shm app:app --bind 0.0.0.0:8000"]