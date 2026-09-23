import os
import sys

# Ensure root folder is in Python path for Vercel serverless imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Entrypoint for Vercel Serverless Function
app = app
