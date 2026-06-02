FROM python:3.11-slim

WORKDIR /app

# Copy data needed by the app
COPY data/processed/ /app/data/processed/

# Copy app source
COPY app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app/streamlit_app.py /app/streamlit_app.py

ENV PORT=8501
ENV API_URL=http://api:8080

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
