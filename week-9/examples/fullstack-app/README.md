# Full-Stack Data Science Application

A complete full-stack application demonstrating all concepts from the course.

## Overview

This example shows:
- Streamlit frontend
- FastAPI backend API
- PostgreSQL database
- Redis caching
- Complete CI/CD pipeline
- Mermaid architecture diagrams
- Production deployment

## Architecture

```mermaid
graph LR
    U[User] --> S[Streamlit App]
    S --> A[FastAPI Backend]
    A --> D[(PostgreSQL)]
    A --> R[(Redis Cache)]
    A --> M[ML Model]
    A --> AG[AI Agent]
    AG --> MCP[MCP Server]
```

## Project Structure

```
fullstack-app/
├── frontend/
│   ├── app.py              # Streamlit application
│   ├── requirements.txt
│   └── Dockerfile
├── backend/
│   ├── main.py             # FastAPI application
│   ├── models.py           # Pydantic models
│   ├── database.py         # Database connection
│   ├── requirements.txt
│   └── Dockerfile
├── tests/
│   ├── test_api.py
│   └── test_frontend.py
├── .github/workflows/
│   ├── ci.yml              # CI pipeline
│   └── deploy.yml          # CD pipeline
└── docker-compose.yml      # Local development
```

## Setup

### Local Development

```bash
# Start all services
podman-compose up

# Services will be available at:
# Frontend: http://localhost:8501
# Backend: http://localhost:8000
# PostgreSQL: localhost:5432
# Redis: localhost:6379
```

### Environment Variables

Create `.env` file:

```bash
# Database
DATABASE_URL=postgresql://user:password@postgres:5432/appdb

# Redis
REDIS_URL=redis://redis:6379

# API Keys (use free tier)
GOOGLE_API_KEY=your-gemini-key
```

## Components

### Frontend (Streamlit)

```python
# frontend/app.py
import streamlit as st
import requests

st.title("Data Science Application")

# User input
user_input = st.text_input("Enter your query:")

if st.button("Submit"):
    # Call backend API
    response = requests.post(
        "http://backend:8000/predict",
        json={"query": user_input}
    )
    
    if response.status_code == 200:
        result = response.json()
        st.success(f"Result: {result['prediction']}")
    else:
        st.error("Error processing request")
```

### Backend (FastAPI)

```python
# backend/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis
from sqlalchemy.orm import Session

app = FastAPI()
redis_client = redis.from_url("redis://redis:6379")

class PredictionRequest(BaseModel):
    query: str

@app.post("/predict")
async def predict(request: PredictionRequest):
    # Check cache
    cached = redis_client.get(request.query)
    if cached:
        return {"prediction": cached, "cached": True}
    
    # Make prediction
    result = model.predict(request.query)
    
    # Cache result
    redis_client.setex(request.query, 3600, result)
    
    # Save to database
    db.add(Prediction(query=request.query, result=result))
    db.commit()
    
    return {"prediction": result, "cached": False}
```

### Database Models

```python
# backend/database.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True)
    query = Column(String)
    result = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
```

## Docker Compose

```yaml
version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "8501:8501"
    environment:
      - BACKEND_URL=http://backend:8000
    depends_on:
      - backend
  
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/appdb
      - REDIS_URL=redis://redis:6379
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    depends_on:
      - postgres
      - redis
  
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=appdb
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## CI/CD Pipeline

### Testing Workflow

```yaml
name: CI

on: [push, pull_request]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
      redis:
        image: redis:7
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r backend/requirements.txt
      - run: pytest backend/tests/
  
  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r frontend/requirements.txt
      - run: pytest frontend/tests/
```

### Deployment Workflow

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: google-github-actions/auth@v1
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
      - run: |
          gcloud run deploy backend \
            --source ./backend \
            --region us-central1
  
  deploy-frontend:
    runs-on: ubuntu-latest
    needs: deploy-backend
    steps:
      - uses: actions/checkout@v3
      - uses: google-github-actions/auth@v1
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
      - run: |
          gcloud run deploy frontend \
            --source ./frontend \
            --region us-central1
```

## Testing

### Backend Tests

```python
# tests/test_api.py
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_predict_endpoint():
    response = client.post(
        "/predict",
        json={"query": "test query"}
    )
    assert response.status_code == 200
    assert "prediction" in response.json()

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
```

### Frontend Tests

```python
# tests/test_frontend.py
from streamlit.testing.v1 import AppTest

def test_app_loads():
    at = AppTest.from_file("frontend/app.py")
    at.run()
    assert not at.exception

def test_submit_button():
    at = AppTest.from_file("frontend/app.py")
    at.run()
    at.text_input[0].set_value("test")
    at.button[0].click()
    assert at.success[0].value
```

## Deployment

### Prerequisites

1. Google Cloud account
2. gcloud CLI installed
3. Service account with Cloud Run permissions

### Deploy Backend

```bash
cd backend
gcloud run deploy backend \
  --source . \
  --region us-central1 \
  --set-env-vars DATABASE_URL=$DATABASE_URL,REDIS_URL=$REDIS_URL
```

### Deploy Frontend

```bash
cd frontend
gcloud run deploy frontend \
  --source . \
  --region us-central1 \
  --set-env-vars BACKEND_URL=$BACKEND_URL
```

## Monitoring

### Health Checks

```python
@app.get("/health")
async def health_check():
    checks = {
        "database": await check_database(),
        "redis": await check_redis(),
        "model": await check_model()
    }
    
    if all(checks.values()):
        return {"status": "healthy", "checks": checks}
    else:
        return {"status": "unhealthy", "checks": checks}, 503
```

### Logging

```python
import structlog

logger = structlog.get_logger()

@app.post("/predict")
async def predict(request: PredictionRequest):
    logger.info("prediction_request", query=request.query)
    
    try:
        result = model.predict(request.query)
        logger.info("prediction_success", result=result)
        return {"prediction": result}
    except Exception as e:
        logger.error("prediction_failed", error=str(e))
        raise HTTPException(500, "Prediction failed")
```

## Architecture Diagrams

### System Flow

```mermaid
sequenceDiagram
    User->>+Frontend: Enter query
    Frontend->>+Backend: POST /predict
    Backend->>+Redis: Check cache
    Redis-->>-Backend: Cache miss
    Backend->>+Model: predict()
    Model-->>-Backend: result
    Backend->>+Database: Save result
    Database-->>-Backend: Saved
    Backend->>+Redis: Cache result
    Redis-->>-Backend: Cached
    Backend-->>-Frontend: Response
    Frontend-->>-User: Display result
```

### Deployment Architecture

```mermaid
graph TB
    GH[GitHub] -->|Push| GA[GitHub Actions]
    GA -->|Build & Test| CR[Cloud Run]
    CR -->|Backend| BE[Backend Service]
    CR -->|Frontend| FE[Frontend Service]
    BE --> DB[(Cloud SQL)]
    BE --> RC[(Redis)]
```

## Performance Optimization

- **Caching**: Redis for frequently accessed data
- **Database**: Connection pooling, indexed queries
- **API**: Async endpoints, parallel processing
- **Frontend**: Streamlit caching for expensive operations

## Security

- Environment variables for secrets
- HTTPS only in production
- Input validation with Pydantic
- Rate limiting on API endpoints
- Database connection encryption

## Common Issues

**Database connection fails**: Check DATABASE_URL is correct
**Redis connection fails**: Ensure Redis is running
**Frontend can't reach backend**: Check BACKEND_URL
**Slow responses**: Check cache hit rate, optimize queries

## Local Development Tips

```bash
# View logs
podman-compose logs -f backend
podman-compose logs -f frontend

# Restart a service
podman-compose restart backend

# Run tests
pytest tests/

# Check database
podman exec -it postgres psql -U user -d appdb
```

## Production Checklist

- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Secrets properly managed
- [ ] Health checks implemented
- [ ] Logging configured
- [ ] Monitoring set up
- [ ] Database migrations tested
- [ ] Load testing completed
- [ ] Documentation updated