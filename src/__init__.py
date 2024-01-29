from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from src.config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'public.index'
login_manager.login_message_category = 'danger'


def create_app(config_class=Config):
    # Initiate app
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.secret_key = 'SECRET_KEY'
    
    CORS(app)
    db.init_app(app)
    login_manager.init_app(app)

    # Import blueprints
    from src.public.routes import public
    from src.errors.handlers import errors
    
    # Register blueprints
    app.register_blueprint(public)
    app.register_blueprint(errors)
    
    # Return the instance of app
    return app
