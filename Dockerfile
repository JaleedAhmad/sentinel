FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

COPY . .

ENV SENTINEL_MODE=dev

EXPOSE 8080

CMD ["python", "app.py"]
