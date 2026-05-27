import os
from app import create_app
from app.extensions import db
from config import ProductionConfig

app = create_app(ProductionConfig)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

# For Gunicorn use: gunicorn flask_app:app