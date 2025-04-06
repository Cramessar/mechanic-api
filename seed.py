# File: seed.py

from application.extensions import db
from application.models import Customer, Mechanic, Inventory, ServiceTicket
from application.utils import hash_password
from datetime import datetime
from random import sample

def seed_db(app):
    with app.app_context():
        print("🔁 Resetting and seeding the database...")

        # Drop and recreate tables on seed_db(app) call
        db.drop_all()
        db.create_all()

        # Add Customers
        customers = [
            Customer(name="Alice", email="alice@example.com", password=hash_password("password1")),
            Customer(name="Bob", email="bob@example.com", password=hash_password("password2")),
            Customer(name="Charlie", email="charlie@example.com", password=hash_password("password3")),
            Customer(name="Diana", email="diana@example.com", password=hash_password("password4")),
            Customer(name="Evan", email="evan@example.com", password=hash_password("password5")),
        ]
        db.session.add_all(customers)

        # Add Mechanics
        mechanics = [
            Mechanic(name="Mike", password=hash_password("mechpass1")),
            Mechanic(name="Nina", password=hash_password("mechpass2")),
            Mechanic(name="Oscar", password=hash_password("mechpass3")),
            Mechanic(name="Paula", password=hash_password("mechpass4")),
            Mechanic(name="Quinn", password=hash_password("mechpass5")),
        ]
        db.session.add_all(mechanics)

        # Add Inventory Items
        parts = [
            Inventory(name="Oil Filter", price=29.99),
            Inventory(name="Brake Pad", price=49.99),
            Inventory(name="Air Filter", price=19.99),
            Inventory(name="Battery", price=89.99),
            Inventory(name="Alternator", price=199.99),
        ]
        db.session.add_all(parts)

        # Create Service Tickets
        for customer in customers:
            ticket = ServiceTicket(
                description=f"{customer.name}'s vehicle needs service",
                status="Pending",
                created_at=datetime.utcnow(),
                customer=customer
            )
            ticket.mechanics = sample(mechanics, 2)
            ticket.parts = sample(parts, 2)
            db.session.add(ticket)

        db.session.commit()
        print("✅ Seed complete: Customers, Mechanics, Inventory, Tickets added!")
