"""Entrypoint shim: keeps ``uvicorn main:app`` working after the move to app/."""
from app.main import app  # noqa: F401
