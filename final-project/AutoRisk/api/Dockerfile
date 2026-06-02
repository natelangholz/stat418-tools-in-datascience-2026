FROM python:3.11-slim

WORKDIR /app

# Data lives next to main.py in the container (/app/data/processed/)
COPY data/processed/vehicle_risk_features_labeled.csv /app/data/processed/vehicle_risk_features_labeled.csv

# Dependencies
COPY api/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY api/main.py /app/main.py

ENV PORT=8080

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--timeout", "120", "main:app"]
