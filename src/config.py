import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('MYSQL_DATABASE_URI')
    SQLALCHEMY_CHARSET = 'utf8mb4'
    SQLALCHEMY_COLLATION = 'utf8mb4_0900_ai_ci'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = os.environ.get('MAIL_PORT')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
