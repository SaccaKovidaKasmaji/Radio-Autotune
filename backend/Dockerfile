
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY database.py .
COPY scraper.py .
COPY firebase_client.py .
COPY frontend ./frontend

RUN ls -la /app
RUN python -c "import main; print('Import OK')"
EXPOSE 8080
CMD ["sh", "-c", "PYTHONPATH=/app python -m uvicorn main:app --host 0.0.0.0 --port 8080"]
