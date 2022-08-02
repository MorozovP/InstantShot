FROM python:3.8-slim

WORKDIR /app

COPY .. /app

RUN pip3 install --upgrade pip -r requirements.txt --no-cache-dir

CMD ["python3", "instant_shot.py"]