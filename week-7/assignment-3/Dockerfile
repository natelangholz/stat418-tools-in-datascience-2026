# part 4a: Run locally with Podman(Dockerfile)

# part a: use python base image
FROM python:3.12-slim

# create working directory
WORKDIR /app


COPY requirements.txt .

# part c: install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# part b: copy application code and model artifact
COPY . .

# part d: expose port 8080
EXPOSE 8080

# part e: start FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
