import os
from app import create_app
from app.extensions import db

# Choose config from environment, default to DevelopmentConfig to avoid
# import-time failures when production environment variables (like a DB URI)
# are not set on the host.
config_name = os.environ.get('FLASK_CONFIG', 'DevelopmentConfig')
app = create_app(config_name)

if __name__ == '__main__':
    # Only reset/create the database in non-production modes to avoid
    # accidentally wiping a production database.
    if config_name != 'ProductionConfig':
        with app.app_context():
            db.drop_all()
            db.create_all()

    app.run(debug=(config_name == 'DevelopmentConfig'))

# For Gunicorn use: gunicorn flask_app:app