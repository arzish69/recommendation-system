import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    API_PREFIX = '/api/v1'
    ALLOWED_ORIGINS = ['http://localhost:3000', 'http://localhost:5000']  # Add your main app URLs
    MODEL_SAVE_PATH = 'app/models/saved/'