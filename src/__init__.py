import os
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from src.config import Config
from itsdangerous import TimestampSigner

db = SQLAlchemy()
mail_manager = Mail()
login_manager = LoginManager()
hash_manager = Bcrypt()
token_manager = TimestampSigner(os.environ.get('MEDIPLUS_SECRET_KEY'))
login_manager.login_view = 'public.login'
login_manager.login_message_category = 'danger'


def create_app(config_class=Config):
    # Initiate app
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.secret_key = os.environ.get('MEDIPLUS_SECRET_KEY')
    
    CORS(app)
    db.init_app(app)
    mail_manager.init_app(app)
    hash_manager.init_app(app)
    login_manager.init_app(app)

    # Import blueprints
    from src.public.routes import public
    from src.error.handlers import error
    from src.manager.routes import manager
    from src.patient.routes import patient
    from src.doctor.routes import doctor
    
    # Register blueprints
    app.register_blueprint(public)
    app.register_blueprint(error)
    app.register_blueprint(manager)
    app.register_blueprint(patient)
    app.register_blueprint(doctor)
    
    # Return the instance of app
    return app
