"""
Vercel serverless function entry point for Flask app
"""
import sys
import os
from pathlib import Path

# Set environment variables BEFORE any imports
os.environ['DISABLE_TESSERACT'] = 'true'
os.environ.setdefault('FLASK_ENV', 'production')

# Add the project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env if it exists
from dotenv import load_dotenv
load_dotenv()

# Import and configure the Flask app
try:
    from app import app
    handler = app
except Exception as e:
    # Fallback error handler if app fails to import
    def handler(request):
        return {
            'statusCode': 500,
            'body': f'Failed to import Flask app: {str(e)}'
        }

