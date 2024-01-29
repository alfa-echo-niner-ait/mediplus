class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:root@localhost:3306/mediplus'
    SQLALCHEMY_CHARSET = 'utf8mb4'
    SQLALCHEMY_COLLATION = 'utf8mb4_0900_ai_ci'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
