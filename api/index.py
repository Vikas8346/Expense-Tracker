"""
Vercel serverless function entry point for Flask app
"""
import sys
import os
from pathlib import Path

# Add the project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import and configure the Flask app
from app import app

# Disable Tesseract for Vercel (not available in serverless)
os.environ['DISABLE_TESSERACT'] = 'true'

# Export app as WSGI handler for Vercel
handler = app
