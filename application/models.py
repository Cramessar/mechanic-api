# File: application/models.py

from datetime import datetime
from application.extensions import db

# junction table: service_ticket <--> mechanic (Many-to-Many)
service_mechanic = db.Table(
    'service_mechanic',
    db.Column('service_ticket_id', db.Integer, db.ForeignKey('service_ticket.id'), primary_key=True),
    db.Column('mechanic_id', db.Integer, db.ForeignKey('mechanic.id'), primary_key=True)
)

# junction table: service_ticket <--> inventory (Many-to-Many)
ticket_parts = db.Table(
    'ticket_parts',
    db.Column('service_ticket_id', db.Integer, db.ForeignKey('service_ticket.id'), primary_key=True),
    db.Column('inventory_id', db.Integer, db.ForeignKey('inventory.id'), primary_key=True)
)



class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)
    #need this for test_customers.py
    tickets = db.relationship("ServiceTicket", backref="customer", lazy=True)


class Mechanic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)
    # need this for test_mechanics.py
    tickets = db.relationship(
        "ServiceTicket",
        secondary=service_mechanic,
        back_populates="mechanics"
    )


class ServiceTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(300), nullable=False)
    status = db.Column(db.String(50), default="Pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)
    # need this for test_service_tickets.py
    mechanics = db.relationship(
        "Mechanic",
        secondary=service_mechanic,
        back_populates="tickets"
    )

    parts = db.relationship(
        "Inventory",
        secondary=ticket_parts,
        back_populates="tickets"
    )

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)

    tickets = db.relationship(
        "ServiceTicket",
        secondary=ticket_parts,
        back_populates="parts"
    )
