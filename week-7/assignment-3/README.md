# Assignment 3: Production API Deployment

**Due:** Before Week 9 class at 6:00 PM 

**Submission:** Pull request to the course repository

## Overview

Build a complete, production-ready API that serves a machine learning model. You'll create a FastAPI application, containerize it with Podman, deploy it to Google Cloud Run, and implement production best practices including authentication, monitoring, and comprehensive documentation.

## Assignment Description

Create a production-ready API that serves a machine learning model (you can use a simple sklearn model like a classifier or regressor trained on any dataset) with:

**Core API Features:**
- Model loading and prediction endpoints
- Batch prediction support
- Health and readiness checks
- Request/response validation with Pydantic
- Comprehensive error handling
- API versioning

**Production Features:**
- Authentication (API key)
- Rate limiting
- CORS configuration
- Logging with request tracking
- Monitoring and metrics
- Automatic API documentation

**Deployment:**
- Containerized with Podman (multi-stage Dockerfile)
- Deployed to Google Cloud Run
- Environment-based configuration
- Secrets management

## Requirements

### Part 1: FastAPI Application

Create `main.py` with your FastAPI application:

**Required Endpoints:**

1. **GET /health** - Health check endpoint
   - Returns 200 if service is running
   - No authentication required

2. **GET /ready** - Readiness check endpoint
   - Returns 200 if model is loaded and ready
   - Returns 503 if not ready
   - No authentication required

3. **POST /v1/predict** - Single prediction endpoint
   - Requires authentication
   - Validates input with Pydantic
   - Returns prediction with confidence score
   - Includes model version in response

4. **POST /v1/predict/batch** - Batch prediction endpoint
   - Requires authentication
   - Accepts multiple instances
   - Returns array of predictions
   - Implements batch size limits (max 100)

5. **GET /v1/model/info** - Model metadata endpoint
   - Returns model version, features, etc.
   - Requires authentication

**Key Functions:**
```python
@app.on_event("startup")
def load_model():
    # Load model at startup
    pass

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/ready")
def readiness_check():
    # Check if model is loaded
    pass

@app.post("/v1/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest, api_key: str = Depends(verify_api_key)):
    # Make prediction
    pass
```

### Part 2: Request/Response Models

Create `models.py` with Pydantic models:

```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional

class PredictionRequest(BaseModel):
    features: List[float] = Field(..., description="Input features")
    model_version: str = Field(default="v1", description="Model version")
    
    @validator('features')
    def validate_features(cls, v):
        # Add your validation logic
        return v

class PredictionResponse(BaseModel):
    prediction: float
    confidence: float
    model_version: str
    request_id: str

class BatchPredictionRequest(BaseModel):
    instances: List[List[float]] = Field(..., max_items=100)
    
class BatchPredictionResponse(BaseModel):
    predictions: List[float]
    count: int
    model_version: str
```

### Part 3: Authentication

Create `auth.py` with authentication logic:

```python
from fastapi import Header, HTTPException
import os

def verify_api_key(api_key: str = Header(...)):
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key
```

### Part 4: Containerization

Create a multi-stage `Dockerfile`:

```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser /app
USER appuser

# Copy installed packages
COPY --from=builder /root/.local /root/.local

# Copy application
COPY --chown=appuser:appuser . .

# Set PATH
ENV PATH=/root/.local/bin:$PATH

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:${PORT:-8080}/health || exit 1

# Cloud Run sets PORT env var
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
```

Create `.dockerignore`:
```
.git
.env
__pycache__
*.pyc
.pytest_cache
.venv
*.pptx
*.pdf
tests/
docs/
```

### Part 5: Configuration

Create `config.py`:

```python
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    api_key: str = os.getenv("API_KEY", "")
    model_path: str = os.getenv("MODEL_PATH", "model.pkl")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    max_batch_size: int = int(os.getenv("MAX_BATCH_SIZE", "100"))
    
    class Config:
        env_file = ".env"

settings = Settings()
```

Create `.env.example`:
```
API_KEY=your_api_key_here
MODEL_PATH=model.pkl
LOG_LEVEL=INFO
MAX_BATCH_SIZE=100
PORT=8080
```

### Part 6: Deployment to Cloud Run

**Build and push with Podman:**

```bash
# Build image
podman build -t myapi .

# Test locally
podman run -p 8080:8080 -e PORT=8080 -e API_KEY=test123 myapi

# Tag for GCR
podman tag myapi gcr.io/PROJECT_ID/myapi

# Push to GCR
podman push gcr.io/PROJECT_ID/myapi
```

**Deploy to Cloud Run:**

```bash
gcloud run deploy myapi \
  --image gcr.io/PROJECT_ID/myapi \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 10 \
  --set-env-vars MODEL_PATH=/app/model.pkl \
  --set-secrets API_KEY=api-key:latest
```

### Part 7: Testing

Create `test_api.py`:

```python
from fastapi.testclient import TestClient
from main import app
import pytest

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_predict_success():
    response = client.post(
        "/v1/predict",
        json={"features": [1.0, 2.0, 3.0]},
        headers={"api-key": "test123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "confidence" in data

def test_predict_no_auth():
    response = client.post(
        "/v1/predict",
        json={"features": [1.0, 2.0, 3.0]}
    )
    assert response.status_code == 403

def test_predict_invalid_input():
    response = client.post(
        "/v1/predict",
        json={"features": []},
        headers={"api-key": "test123"}
    )
    assert response.status_code == 422
```

### Part 8: Documentation

#### README.md
Must include:
- Project overview
- API endpoints documentation
- Setup instructions (local and cloud)
- Authentication instructions
- Example requests with curl/Python
- Environment variables
- Deployment instructions
- Testing instructions

#### API_DOCUMENTATION.md
Must include:
- Detailed endpoint descriptions
- Request/response schemas
- Example requests and responses
- Error codes and meanings
- Rate limiting information
- Authentication flow

## Technical Requirements

### Directory Structure
```
week-7/assignment-3/submissions/yourname/
├── README.md
├── API_DOCUMENTATION.md
├── requirements.txt
├── .env.example
├── .dockerignore
├── Dockerfile
├── main.py
├── models.py
├── auth.py
├── config.py
├── model.pkl (or your model file)
├── tests/
│   └── test_api.py
└── deployment/
    ├── deploy.sh
    └── cloud-run-config.yaml
```

### Code Quality
- Use type hints for all function signatures
- Include docstrings for all functions and classes
- Follow PEP 8 style guidelines
- Use meaningful variable names
- Implement proper error handling
- Add logging throughout the application
- Write tests for all endpoints

### Dependencies

Create `requirements.txt`:
```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.0.0
python-multipart>=0.0.6
python-jose[cryptography]>=3.3.0
slowapi>=0.1.9
scikit-learn>=1.3.0
joblib>=1.3.0
pandas>=2.0.0
numpy>=1.24.0
pytest>=7.4.0
httpx>=0.25.0
```

Install with uv:
```bash
uv pip install -r requirements.txt
```

## Deployment Checklist

Before submitting, verify:

- [ ] API runs locally with `uvicorn main:app --reload`
- [ ] All endpoints work and return correct responses
- [ ] Authentication is implemented and working
- [ ] Input validation catches invalid data
- [ ] Error handling returns appropriate status codes
- [ ] Health and readiness checks work
- [ ] Tests pass with `pytest`
- [ ] Container builds successfully with Podman
- [ ] Container runs locally
- [ ] API is deployed to Cloud Run
- [ ] Deployed API is accessible via HTTPS
- [ ] Environment variables are set correctly
- [ ] Secrets are in Secret Manager (not in code)
- [ ] API documentation is complete
- [ ] README has clear setup instructions

## Submission Instructions

1. **Create a feature branch:**
   ```bash
   git checkout -b hw3-yourname
   ```

2. **Create your assignment directory:**
   ```bash
   mkdir -p week-7/assignment-3/submissions/yourname
   cd week-7/assignment-3/submissions/yourname
   ```

3. **Develop your assignment:**
   - Write code incrementally
   - Test each component separately
   - Commit frequently with meaningful messages

4. **Required files:**
   - All Python scripts (main.py, models.py, auth.py, config.py)
   - README.md with complete documentation
   - API_DOCUMENTATION.md with endpoint details
   - requirements.txt
   - Dockerfile
   - .dockerignore
   - .env.example (template for environment variables)
   - tests/test_api.py
   - Your trained model file
   - deployment/deploy.sh script

5. **Do NOT include:**
   - .env file (contains secrets!)
   - __pycache__ directories
   - .venv directories
   - Large data files
   - Your actual API keys

6. **Test your deployment:**
   ```bash
   # Test locally
   uvicorn main:app --reload
   
   # Test with curl
   curl -X POST http://localhost:8000/v1/predict \
     -H "Content-Type: application/json" \
     -H "api-key: your_key" \
     -d '{"features": [1.0, 2.0, 3.0]}'
   
   # Run tests
   pytest tests/
   ```

7. **Commit and push:**
   ```bash
   git add .
   git commit -m "Add assignment 3 submission - yourname"
   git push origin hw3-yourname
   ```

8. **Create a pull request:**
   - Base: `assignment-3`
   - Compare: `hw3-yourname`
   - Title: "Assignment 3 - Your Name"
   - Description: Include:
     - Your deployed API URL
     - Brief description of your model
     - Any special setup instructions
     - Known limitations

## Example Code Snippets

### Complete FastAPI App Template

```python
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import joblib
import logging
import uuid
from models import PredictionRequest, PredictionResponse
from auth import verify_api_key
from config import settings

# Setup logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

# Create app
app = FastAPI(
    title="My ML API",
    description="Production ML model API",
    version="1.0.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Global model variable
model = None

@app.on_event("startup")
def load_model():
    global model
    try:
        model = joblib.load(settings.model_path)
        logger.info(f"Model loaded from {settings.model_path}")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/ready")
def readiness_check():
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "ready"}

@app.post("/v1/predict", response_model=PredictionResponse)
@limiter.limit("100/minute")
def predict(
    request: PredictionRequest,
    api_key: str = Depends(verify_api_key)
):
    try:
        prediction = model.predict([request.features])[0]
        confidence = model.predict_proba([request.features]).max()
        
        return PredictionResponse(
            prediction=float(prediction),
            confidence=float(confidence),
            model_version="v1.0",
            request_id=str(uuid.uuid4())
        )
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail="Prediction failed")
```

## Resources

### FastAPI
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Uvicorn Documentation](https://www.uvicorn.org/)

### Containerization
- [Podman Documentation](https://podman.io/docs)
- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/)

### Deployment
- [Google Cloud Run Docs](https://cloud.google.com/run/docs)
- [Cloud Run Quickstart](https://cloud.google.com/run/docs/quickstarts)
- [Secret Manager](https://cloud.google.com/secret-manager/docs)

### Testing
- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

## Common Issues and Solutions

### Issue: Model not loading
**Solution:** Check file path, ensure model file is in container, verify permissions

### Issue: Authentication not working
**Solution:** Verify API key is set in environment, check header name matches

### Issue: Container fails to start
**Solution:** Check logs with `podman logs`, verify PORT environment variable

### Issue: Cloud Run deployment fails
**Solution:** Check image is pushed to GCR, verify project ID, check IAM permissions

### Issue: API returns 503
**Solution:** Check readiness endpoint, verify model loaded successfully