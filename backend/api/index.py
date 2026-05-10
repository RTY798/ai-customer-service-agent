# Vercel Python serverless entry point
import sys
import os

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.knowledge_base.loader import seed_knowledge_base
from app.main import app

# Pre-load knowledge base on cold start
seed_knowledge_base()
