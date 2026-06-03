import os

import requests
import streamlit as st


BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

st.title("Full-Stack Iris Classifier Demo")
st.write("Enter flower measurements and send them to the FastAPI backend for prediction.")

sepal_length = st.number_input("Sepal length (cm)", min_value=0.1, value=5.1, step=0.1)
sepal_width = st.number_input("Sepal width (cm)", min_value=0.1, value=3.5, step=0.1)
petal_length = st.number_input("Petal length (cm)", min_value=0.1, value=1.4, step=0.1)
petal_width = st.number_input("Petal width (cm)", min_value=0.1, value=0.2, step=0.1)

if st.button("Predict species"):
    payload = {
        "sepal_length": sepal_length,
        "sepal_width": sepal_width,
        "petal_length": petal_length,
        "petal_width": petal_width,
    }
    response = requests.post(f"{BACKEND_URL}/predict", json=payload, timeout=10)
    if response.ok:
        result = response.json()
        st.success(f"Predicted species: {result['prediction']}")
        st.write(f"Cached: {result['cached']}")
        st.json(result)
    else:
        st.error("Backend request failed")

if st.button("Load history"):
    response = requests.get(f"{BACKEND_URL}/history", timeout=10)
    if response.ok:
        st.json(response.json())
    else:
        st.error("Could not load history")

