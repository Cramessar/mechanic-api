# File: application/blueprints/service_tickets/schemas.py

from application.extensions import ma
from application.models import ServiceTicket
from marshmallow import EXCLUDE, fields


class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    customer = fields.Nested("CustomerSchema", exclude=("tickets",))
    mechanics = fields.Nested("MechanicSchema", many=True)
    parts = fields.Nested("InventorySchema", many=True)

    class Meta:
        model = ServiceTicket
        load_instance = True
        include_relationships = True
        unknown = EXCLUDE

ticket_schema = ServiceTicketSchema()
tickets_schema = ServiceTicketSchema(many=True)
