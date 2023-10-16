FROM python:3.10

WORKDIR /app

ADD . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["gunicorn", "--worker-tmp-dir", "/dev/shm", "app:app", "--bind", "0.0.0.0:8000"]