from flask import Flask
from .extensions import db, ma, limiter, cache
try:
    from flask_swagger_ui import get_swaggerui_blueprint

    SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
    API_URL = '/static/swagger.yaml'  # Our API URL (can of course be a local resource)

    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Your API's Name"
        }
    )
except Exception:
    swaggerui_blueprint = None

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(f'config.{config_name}')

    db.init_app(app)
    ma.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)
    # register blueprints (imports must happen after app is created)
    from .blueprints.customers import customers_bp
    from .blueprints.mechanics import mechanics_bp
    from .blueprints.service_tickets import service_tickets_bp
    from .blueprints.inventory import inventory_bp

    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(mechanics_bp, url_prefix='/mechanics')
    app.register_blueprint(service_tickets_bp, url_prefix='/service-tickets')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')

    # Register Swagger UI blueprint if available
    if swaggerui_blueprint:
        app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    return app