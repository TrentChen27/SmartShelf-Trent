import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours

    # Cloudflare R2
    R2_ACCOUNT_ID = os.getenv('R2_ACCOUNT_ID')
    R2_ACCESS_KEY_ID = os.getenv('R2_ACCESS_KEY_ID')
    R2_SECRET_ACCESS_KEY = os.getenv('R2_SECRET_ACCESS_KEY')
    R2_ENDPOINT_URL = os.getenv('R2_ENDPOINT_URL')
    R2_BUCKET_NAME = os.getenv('R2_BUCKET_NAME', 'smartshelf-products')

    # Flask
    DEBUG = os.getenv('FLASK_ENV') == 'development'
