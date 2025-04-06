# File: application/blueprints/inventory/schemas.py

from application.extensions import ma
from application.models import Inventory

class InventorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory
        load_instance = True
