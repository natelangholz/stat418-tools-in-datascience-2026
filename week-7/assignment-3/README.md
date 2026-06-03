# stats418-assignment3-fastapi

## Project Overview
The project creates a standalone GitHub repository that builds and serves a machine learning model trained on the mtcars dataset.  The project exposes the model through FastAPI. containerizes it in Docker, and deploys it to Google Cloud Run.(Initial project completed on Windows 11)

## Model Description
The model is a linear regression model that predicts mpg on horsepower, weight, cylinder count, gears, and whether or not the car is manual.

## To build the image
Navigate to project directory in Powershell or Command Prompt
run "docker build -t mtcars-fastapi ."
run "docker run -p 8080:8080 mtcars-fastapi"

## To run locally
Then open the app at http://localhost:8080/docs 
To predict using the model locally at http://localhost:8080/docs, expand POST/predict -> click Try it out -> input values to Edit Value -> Execute and you get a prediction.

## To Tag and push image
In Powershell
run "docker login"
Enter username and password
run "docker tag mtcars-fastapi <username>/mtcars-fastapi:latest"
run "docker push juliafung/mtcars-fastapi:latest"

## To deploy to cloud run
In Powershell,
run "gcloud auth login"(should see You are now logged in as [<your email>])
In google cloud, click box to the right of the Google Cloud logo and click new project.
Choose project name(<name>-mtcars-fastapi) then click Create.
Then using the ID usually the project name you chose, run "gcloud artifacts repositories create fastapi-repo --repository-format=docker --location=us-central1 --description="FastAPI container repo""
In Docker Desktop, make sure under settings -> resources -> WSL integration, Enable integration with my default WSL distro is checked and  WSL distro you have is toggled ON.
In Powershell, run "gcloud auth configure-docker us-central1-docker.pkg.dev" and choose Y.
Run "docker push us-central1-docker.pkg.dev/<name>-mtcars-fastapi/fastapi-repo/mtcars-fastapi:latest" in Powershell.
Run "gcloud run deploy mtcars-fastapi --image us-central1-docker.pkg.dev/<name>-mtcars-fastapi/fastapi-repo/mtcars-fastapi:latest --platform managed --region us-central1 --allow-unauthenticated --port 8080" in Powershell.

## Verify API
Check health at https://mtcars-fastapi-678323048980.us-central1.run.app/health, which should say "{"status":"ok"}".
Check ready at https://mtcars-fastapi-678323048980.us-central1.run.app/ready, which should say "{"ready":true,"detail":"Model loaded and ready"}".

Finally, https://mtcars-fastapi-678323048980.us-central1.run.app/docs has FastAPI app.

## Repository structure explanation
The repository contains the data, Docker file, requirements.txt, and app, model, scripts, and tests folders.  The app folder contains the script main.py that defines the FastAPI application.  The models folder contains the saved model in model.pkl.  The scripts folder contains the train_model.py script that trains the model and saves it to the pkl file.  The tests folder contains the test_api.py script that includes and automated test of the API's heath and a prediction request.

curl -X POST "https://mtcars-fastapi-678323048980.us-central1.run.app/docs/predict" \
  -H "Content-Type: application/json" \
  -d '{
        "cyl": 4,
        "hp": 100,
        "wt": 2.5,
        "gear": 5,
        "am": 0
      }'

## To test
Navigate to preject directory in Powershell.
Activate virtual environment.
Run "pytest -q" and should get "2 passed"