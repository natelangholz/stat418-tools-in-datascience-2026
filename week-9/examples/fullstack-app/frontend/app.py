import os

import requests
import streamlit as st


BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

st.title("Full-Stack Data Science Demo")

query = st.text_input("Enter a query", "Test query")

if st.button("Submit"):
    response = requests.post(f"{BACKEND_URL}/predict", json={"query": query}, timeout=10)
    if response.ok:
        result = response.json()
        st.success(f"Prediction: {result['prediction']}")
        st.write(f"Cached: {result['cached']}")
    else:
        st.error("Backend request failed")

if st.button("Load history"):
    response = requests.get(f"{BACKEND_URL}/history", timeout=10)
    if response.ok:
        st.json(response.json())
    else:
        st.error("Could not load history")

