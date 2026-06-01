# Basic CI/CD Example

This example is a small FastAPI service plus GitHub Actions workflow files that demonstrate a practical CI/CD pipeline for a course-sized project.

## What this example includes

- `app.py` — FastAPI app with:
  - `GET /health`
  - `POST /predict`
- `test_app.py` — pytest-based API tests
- `requirements.txt` — app, test, lint, and format dependencies
- `Dockerfile` — container image for local runs or deployment
- `ci.yml` — example continuous integration workflow
- `deploy.yml` — example deployment workflow for Google Cloud Run

## Why this is useful

This example shows the minimum pieces needed to move from:
1. writing a small API,
2. testing it automatically,
3. packaging it in a container,
4. and deploying it through GitHub Actions.

It is intentionally simple so students can see the pipeline structure clearly.

## FastAPI app behavior

### Health endpoint

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status":"ok"}
```

### Prediction endpoint

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"feature1": 2.0, "feature2": 4.0, "feature3": 6.0}'
```

Expected response shape:

```json
{
  "prediction": 4.0
}
```

## Local setup

```bash
cd week-9/examples/basic-cicd
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run locally

Because `app.py` includes a Python entrypoint, you can start it with:

```bash
python app.py
```

Then visit:

- API: `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`

## Run tests and quality checks

```bash
pytest -q
ruff check .
black --check .
```

## Build and run container locally

```bash
podman build -t basic-cicd-example .
podman run -p 8000:8000 basic-cicd-example
```

Then test:

```bash
curl http://localhost:8000/health
```

## CI workflow overview

The `ci.yml` file demonstrates a standard CI sequence:

- check out the repository
- install Python
- install dependencies
- run tests
- run Ruff
- run Black in check mode

That gives fast feedback whenever code is pushed or a pull request is opened.

## Deploy workflow overview

The `deploy.yml` file shows the structure of a deployment job that can:

- authenticate to Google Cloud,
- build a deployable container,
- deploy the app to Cloud Run.

In a real repository, secrets such as service account credentials would be stored in GitHub repository secrets.



## Notes

- The workflow files live directly in this teaching example directory so students can read them easily.
- In a production GitHub repository, these files would normally live under `.github/workflows/`.
