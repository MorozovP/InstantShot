FROM python:3.7-slim

WORKDIR /app

COPY .. /app

RUN pip3 install --upgrade pip -r requirements.txt --no-cache-dir

CMD ["gunicorn", "db-api.wsgi:application", "--bind", "0:8000" ]