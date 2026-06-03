from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import os
from contextlib import asynccontextmanager

# Part 2: FastAPI Application
@asynccontextmanager
async def lifespan(app: FastAPI):
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    filepath_model = os.path.join(base, "models", "model.pkl")
    try: 
        with open(filepath_model, "rb") as f:
            app.state.model = pickle.load(f)
        print("Model loaded successfully")
    except FileNotFoundError:
        app.state.model = None
        print("Model file(model.pkl) not found")
    # part 3c: graceful handling if the model cannot load
    except Exception as e:
        app.state.model = None
        print(f"Error loading model: {e}")
    yield
    print("Shutting down")

# part 3: validate input with pydantic
class CarFeatures(BaseModel):
    cyl: int
    hp: int
    wt: float
    gear: int
    am: int

class PredictionResponse(BaseModel):
    predicted_mpg: float

app = FastAPI(lifespan = lifespan)

# part 2: GET /ready
@app.get("/ready")
def ready():
    model = getattr(app.state, "model", None)
    # prt b: returns a non-200 response if the model is missing
    if model is None:
        return {'ready': False, "detail": "Model not loaded"}, 503
    # part a: return success response if model is loaded and ready
    return {"ready": True, "detail": "Model loaded and ready"}

# part 3: POST /predict
@app.post("/predict")
# part a: accepts input values for the predictor variables in model
def predict(features: CarFeatures): # part 3a: pydantic request validation
    model = getattr(app.state, "model", None)
    if model is None:
        return {'error': "Model not loaded"}, 503
    X = [[features.cyl, features.hp, features.wt, features.gear, features.am]]
    pred = model.predict(X)[0]
    # part c: returns the predicted mpg
    return PredictionResponse(
        predicted_mpg = float(pred)
    )

# part 1: GET /health
@app.get("/health")
def health():
    # part a/b: return success response if API is running authentication not required
    return {"status": "ok"}


