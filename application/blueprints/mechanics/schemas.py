# File: application/blueprints/mechanics/schemas.py

from application.extensions import ma
from application.models import Mechanic
from marshmallow import EXCLUDE

class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
        load_instance = True
        unknown = EXCLUDE
        include_relationships = True 
        exclude = ("password",) 

mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)
