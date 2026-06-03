# Assignment 3: MTCARS FastAPI Deployment

**Due:** Before Week 9 class at 6:00 PM

**Submission:** Pull request to the `assignment-3` branch in the main course repository

## Overview

Create a standalone GitHub repository that builds and serves a machine learning model trained on the `mtcars.csv` dataset. Your project must use Python, FastAPI, and Podman. You will train a predictive linear regression model with `mpg` as the response variable and one or more of the remaining variables as predictors, expose the model through an API, containerize it, and deploy it.

This assignment is intentionally specific so that everyone works from the same dataset and the same general deployment stack while still having room for different modeling and implementation choices.

## Assignment Description

Create a standalone GitHub repo for an **MTCARS FastAPI API**. In that repository, you must:

1. Use the provided `mtcars.csv` dataset
2. Train a predictive linear model in Python with:
   - response variable: `mpg`
   - predictors: any one or more of the remaining variables
3. Build a FastAPI application that serves predictions from that model
4. Run the API locally with Podman
5. Push your container image to a registry
6. Deploy the API to Google Cloud Run
7. Make the repo reproducible so someone can clone it and run it themselves

You may keep the project simple, but it must be complete and reproducible.

## Required Dataset

Use the dataset included with this assignment:

- `week-7/assignment-3/mtcars.csv`

Your standalone repo should also include a copy of `mtcars.csv` so the work is self-contained.

## Required Deliverable Structure in Your Standalone Repo

Your standalone GitHub repo should contain, at minimum:

```text
your-mtcars-fastapi-repo/
├── README.md
├── mtcars.csv
├── Dockerfile
├── .dockerignore
├── requirements.txt or pyproject.toml
├── app/
│   └── main.py
├── models/
│   └── model.pkl
├── notebooks/ or scripts/
│   └── training workflow
└── tests/
    └── test_api.py
```

You may organize your repo differently if it is clean and well documented.

## Part 1: Modeling Requirements

Train a linear regression model in Python using `mtcars.csv`.

### Minimum modeling requirements

- Load `mtcars.csv`
- Use `mpg` as the response
- Use at least 1 predictor variable
- Train a regression model in Python
- Save the trained model to disk
- Clearly document which predictors you used

### Recommended libraries

You may use:
- `pandas`
- `scikit-learn`
- `joblib` or `pickle`

### Suggested workflow

You can train the model in:
- a notebook, or
- a Python script

Your repo must make it clear how the model artifact was created.

## Part 2: FastAPI Application

Create a FastAPI application that loads the trained model and serves predictions.

### Required endpoints

1. **GET `/health`**
   - returns a success response if the API is running
   - no authentication required

2. **GET `/ready`**
   - returns a success response if the model is loaded and ready
   - returns a non-200 response if the model is missing or unavailable

3. **POST `/predict`**
   - accepts input values for the predictor variables used by your model
   - validates input with Pydantic
   - returns the predicted `mpg`

### Example structure

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class PredictionRequest(BaseModel):
    wt: float
    hp: float

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
def predict(request: PredictionRequest):
    return {"predicted_mpg": 21.3}
```

## Part 3: Input Validation and Error Handling

Your API must include:

- Pydantic request validation
- helpful errors for invalid input
- graceful handling if the model cannot be loaded

At minimum:
- invalid types should return a validation error
- missing required predictors should return a validation error
- missing model file should be handled clearly

## Part 4: Run Locally with Podman

Your project must run locally in a container with Podman.

### Required files

#### `Dockerfile`
Your Dockerfile must:
- use a Python base image
- copy the application code and model artifact
- install dependencies
- expose port `8080`
- start the FastAPI app

#### `.dockerignore`
Should exclude unnecessary files such as:
- `.git`
- `.venv`
- `__pycache__`
- notebook checkpoints
- secrets

### Required Podman workflow

Your README must include commands similar to:

```bash
podman build -t mtcars-fastapi .
podman run --rm -p 8080:8080 mtcars-fastapi
```

You should test locally before deploying.

## Part 5: Deployment

Deploy your containerized API to Google Cloud Run.

Your README must include:
- how to build the image
- how to run it locally
- how to tag and push the image
- how to deploy it to Cloud Run
- your deployed API URL

## Part 6: Reproducibility and Documentation

Someone else should be able to:
- clone your repo
- install dependencies
- rebuild your model
- run your API locally
- call your API successfully
- understand what files are doing what

### Your README must include

- project overview
- description of the model
- variables used for prediction
- local setup instructions
- Podman build and run commands
- API endpoint documentation
- example request and response
- deployment instructions
- deployed API URL
- short explanation of repo structure

### Required example API call

Provide at least one working `curl` example in your README.

For example:

```bash
curl -X POST "http://localhost:8080/predict" \
  -H "Content-Type: application/json" \
  -d '{"wt": 2.62, "hp": 110}'
```

The response should show a predicted `mpg`.

## Part 7: Testing

Include at least one automated API test.

Minimum:
- test `/health`
- test one successful `/predict` request

Recommended:
- test invalid input
- test missing field behavior
- test readiness endpoint

## Part 8: Production-Oriented Features

Keep the project practical and specific, but include several production-minded features.

You should include or clearly discuss as many of the following as make sense for your project:

- health check endpoint
- readiness check endpoint
- request/response validation with Pydantic
- clear error handling
- automatic FastAPI docs
- environment-based configuration
- containerization with Podman
- deployment documentation
- tests
- logging

You do **not** need to make this artificially complicated. Authentication, rate limiting, and advanced monitoring are welcome but optional.

## Technical Requirements

### Your standalone repo should include

- FastAPI app
- trained model artifact
- model training workflow
- `mtcars.csv`
- `Dockerfile`
- `.dockerignore`
- dependency file
- README
- at least one automated test

### Code quality expectations

- use clear file organization
- use meaningful variable names
- include type hints where appropriate
- write readable, reproducible code
- keep secrets out of version control

## Submission Instructions

You are submitting **a link to your standalone GitHub repository**, not all project files directly into this course repo.

### Step 1: Create your standalone repo

Create a new GitHub repository with a clear name, for example:

- `mtcars-fastapi-api`
- `assignment-3-mtcars-fastapi`
- `mtcars-ml-api`

### Step 2: Build your project in that repo

Make sure the repo includes:
- your code
- your model artifact
- your dataset
- your documentation

### Step 3: Submit to this course repo

Inside this course repository, create a markdown file in:

```text
week-7/assignment-3/submissions/
```

Name it:

```text
your-name-hw3.md
```

That markdown file should include:
- your name
- assignment title
- a link to your standalone repo
- a link to your deployed API
- a short note about which predictors you used

### Step 4: Open your pull request

Create a pull request:
- base branch: `assignment-3`
- compare branch: your feature branch
- title: `Assignment 3 - Your Name`

## Deployment Checklist

Before submitting, verify:

- [ ] model trained from `mtcars.csv`
- [ ] `mpg` used as the response
- [ ] FastAPI app works locally
- [ ] `/health` works
- [ ] `/ready` works
- [ ] `/predict` works
- [ ] request validation works
- [ ] Podman container builds successfully
- [ ] Podman container runs locally
- [ ] API deployed to Cloud Run
- [ ] README is complete
- [ ] at least one automated test is included
- [ ] repo is reproducible for another user

## Suggested Local Workflow

```bash
# create virtual environment
uv venv
source .venv/bin/activate

# install dependencies
uv pip install -r requirements.txt

# train your model
python train_model.py

# run locally
python -m app.main

# or build container
podman build -t mtcars-fastapi .

# run container
podman run --rm -p 8080:8080 mtcars-fastapi
```

## Resources

### FastAPI
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

### Modeling
- [scikit-learn Documentation](https://scikit-learn.org/stable/)

### Containerization
- [Podman Documentation](https://podman.io/docs)

### Deployment
- [Google Cloud Run Docs](https://cloud.google.com/run/docs)

## Common Issues

### Model file not found
Make sure your trained model is saved in the location expected by your API.

### Container runs but API fails
Check your application startup command, port, and model path.

### Local request fails
Check that your request JSON matches the predictor names and types expected by your Pydantic model.

### Deployment differs from local
Make sure the same model artifact and environment variables are available in the deployed container.