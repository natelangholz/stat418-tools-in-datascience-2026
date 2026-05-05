# Basic CI/CD Pipeline

A complete GitHub Actions CI/CD pipeline for a data science project.

## Overview

This example demonstrates:
- Automated testing on every push
- Code quality checks (linting, formatting)
- Building container images with Podman
- Deploying to Google Cloud Run
- Environment-specific configurations

## Files

- `.github/workflows/ci.yml` - CI pipeline (test, lint)
- `.github/workflows/deploy.yml` - CD pipeline (deploy)
- `tests/` - Test suite
- `Dockerfile` - Container configuration
- `requirements.txt` - Python dependencies

## Setup

```bash
# Clone and install
git clone <your-repo>
cd basic-cicd
pip install -r requirements.txt

# Run tests locally
pytest

# Run linting
ruff check .
black --check .
```

## GitHub Actions Workflows

### CI Pipeline (`.github/workflows/ci.yml`)

Runs on every push and pull request:

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'
      - run: pip install -r requirements.txt
      - run: pytest --cov=. --cov-report=xml
      
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install ruff black
      - run: ruff check .
      - run: black --check .
```

### CD Pipeline (`.github/workflows/deploy.yml`)

Deploys to Cloud Run when tests pass on main branch:

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    needs: test  # Wait for tests to pass
    steps:
      - uses: actions/checkout@v3
      
      - uses: google-github-actions/auth@v1
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
      
      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy my-app \
            --source . \
            --region us-central1 \
            --allow-unauthenticated
```

## Setting Up Secrets

1. Go to GitHub repository Settings → Secrets → Actions
2. Add secrets:
   - `GCP_SA_KEY`: Google Cloud service account key (JSON)
   - `API_KEY`: Any API keys your app needs

## Testing

### Unit Tests

```python
# tests/test_utils.py
def test_preprocess():
    from utils import preprocess
    assert preprocess("  hello  ") == "hello"

def test_validate_input():
    from utils import validate_input
    assert validate_input({"value": 1}) == True
    assert validate_input({}) == False
```

### Integration Tests

```python
# tests/test_api.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_predict_endpoint():
    response = client.post(
        "/predict",
        json={"features": [1.0, 2.0, 3.0]}
    )
    assert response.status_code == 200
    assert "prediction" in response.json()
```

## Code Quality

### Linting with Ruff

```bash
# Check for issues
ruff check .

# Auto-fix issues
ruff check --fix .
```

### Formatting with Black

```bash
# Check formatting
black --check .

# Format code
black .
```

## Deployment

### Local Testing

```bash
# Build container
podman build -t my-app .

# Run locally
podman run -p 8000:8000 my-app

# Test
curl http://localhost:8000/health
```

### Deploy to Cloud Run

Automatic deployment happens when you push to main branch and tests pass.

Manual deployment:

```bash
gcloud run deploy my-app \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

## Monitoring

### View Logs

```bash
# GitHub Actions logs
# Go to Actions tab in GitHub

# Cloud Run logs
gcloud run services logs read my-app --region us-central1
```

### Check Status

```bash
# Get service URL
gcloud run services describe my-app --region us-central1 --format='value(status.url)'

# Test health endpoint
curl https://your-app-url/health
```

## Workflow Triggers

The CI/CD pipeline runs on:
- **Every push**: Runs tests and linting
- **Every pull request**: Runs tests and linting
- **Push to main**: Runs tests, linting, and deploys

## Caching

The workflow caches pip dependencies to speed up builds:

```yaml
- uses: actions/setup-python@v4
  with:
    python-version: '3.11'
    cache: 'pip'  # Automatically caches based on requirements.txt
```

## Best Practices

- **Fast feedback**: Tests run in parallel with linting
- **Fail fast**: Pipeline stops on first failure
- **Caching**: Dependencies are cached for speed
- **Secrets**: Never commit secrets, use GitHub Secrets
- **Testing**: Test locally before pushing
- **Monitoring**: Check logs after deployment

## Common Issues

**Tests fail in CI but pass locally**: Check Python version matches
**Deployment fails**: Verify GCP_SA_KEY secret is set correctly
**Slow pipeline**: Add caching, parallelize jobs
**Import errors**: Ensure all dependencies in requirements.txt

