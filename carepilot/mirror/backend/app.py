#!/usr/bin/env python3
"""Standalone launcher — imports the modular CarePilot app and runs uvicorn.
Run: python3 app.py   (server on :8000)"""
from main import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
