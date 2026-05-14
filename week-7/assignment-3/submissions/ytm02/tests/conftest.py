"""Configure sys.path and environment for pytest."""
import sys
import os

# Add the submission root to path so `from main import app` works
SUBMISSION_DIR = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.abspath(SUBMISSION_DIR))

# Set env vars before any app modules are imported
os.environ.setdefault("API_KEY", "test123")
os.environ.setdefault("MODEL_PATH", os.path.abspath(os.path.join(SUBMISSION_DIR, "model.pkl")))
