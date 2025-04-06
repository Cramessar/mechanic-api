# File: application/blueprints/customers/schemas.py

from application.extensions import ma
from application.models import Customer
from marshmallow import EXCLUDE, fields
from marshmallow_sqlalchemy import auto_field
from marshmallow import Schema

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    password = fields.String(load_only=True)

    class Meta:
        model = Customer
        load_instance = True
        include_relationships = True  
        exclude = ()  
        unknown = EXCLUDE

    id = auto_field()
    name = auto_field()
    email = auto_field()

class CustomerLoginSchema(Schema): 
    email = fields.Email(required=True)
    password = fields.String(required=True)

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
login_schema = CustomerLoginSchema()
