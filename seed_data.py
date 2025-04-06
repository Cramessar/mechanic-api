# File: seed_data.py
# Run this file to populate or clean db to default state.
# seed.py shows all the info that will populate.

from flask_app import app
from seed import seed_db

with app.app_context():
    seed_db(app)
