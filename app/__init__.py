from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.routes.api import api_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config['ALLOWED_ORIGINS'],
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix=app.config['API_PREFIX'])
    
    return app