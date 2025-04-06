# File: application/__init__.py

from flask import Flask
from flask_migrate import Migrate
from flasgger import Swagger
from config import Config
from application.extensions import db, ma, limiter, cache

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    print(f"🛠️ App Config: DEBUG={app.config['DEBUG']}")

    # extensions
    db.init_app(app)
    ma.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)
    Migrate(app, db)

    # Swagger setup with separated template and config
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "Mechanic API",
            "description": "Auto repair management system API documentation.",
            "version": "1.0.0"
        },
        "host": "mechanic-api-ewyr.onrender.com",
        "schemes": ["https"]
    }

    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec_1',
                "route": '/apispec_1.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "swagger_ui": True,
        "specs_route": "/apidocs"
    }

    Swagger(app, template=swagger_template, config=swagger_config)

    # Register blueprints double check the names of the blueprints in the routes files if you get a build error. look at service-tickets
    from application.blueprints.customers.routes import customers_bp
    from application.blueprints.mechanics.routes import mechanics_bp
    from application.blueprints.service_tickets.routes import service_tickets_bp
    from application.blueprints.inventory.routes import inventory_bp

    app.register_blueprint(customers_bp, url_prefix="/customers")
    app.register_blueprint(mechanics_bp, url_prefix="/mechanics")
    app.register_blueprint(service_tickets_bp, url_prefix="/service-tickets")
    app.register_blueprint(inventory_bp, url_prefix="/inventory")

    @app.route("/")
    def index():
        return {"message": "Welcome to the Mechanic API!"}

    #this is just for testing purposes but we all know its really a sanity check and its probably here to stay.
    @app.route("/config-check")
    def config_check():
        return {
            "Prod Config Test": ["Only show this when you visit localhost:5000/config-check"],
            "Does this work?": ["Yes Dummy you are a good programmer..."]
        }

    return app
