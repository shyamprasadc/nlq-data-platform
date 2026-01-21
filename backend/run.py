#!/usr/bin/env python3
"""
Runner script for the FastAPI backend server.

Usage (from project root):
    PYTHONPATH=. python backend/run.py

Or use the recommended command:
    PYTHONPATH=. python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
"""

import os
import sys
from pathlib import Path

# Ensure project root is in PYTHONPATH for uvicorn reload subprocess
project_root = str(Path(__file__).parent.parent)
os.environ["PYTHONPATH"] = project_root

import uvicorn

if __name__ == "__main__":
    os.chdir(project_root)  # Change to project root
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
