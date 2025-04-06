# File: seed_data.py
from flask_app import app
from seed import seed_db

with app.app_context():
    seed_db(app)
