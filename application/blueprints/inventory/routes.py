# File: application/blueprints/inventory/routes.py

from flask import Blueprint, request, jsonify
from application.extensions import db, limiter, cache
from application.models import Inventory, ServiceTicket
from application.utils import mechanic_token_required
from .schemas import InventorySchema

inventory_bp = Blueprint("inventory", __name__)


inventory_schema = InventorySchema()
inventory_list_schema = InventorySchema(many=True)


@inventory_bp.route("/", methods=["GET"])
@cache.cached(timeout=60)
def get_all_parts():
    """
    Get all inventory parts
    ---
    tags:
      - Inventory
    summary: Retrieve all inventory parts
    description: Returns a list of all inventory items available in the shop.
    responses:
      200:
        description: A list of inventory parts
        schema:
          type: array
          items:
            $ref: '#/definitions/Inventory'
    """
    parts = Inventory.query.all()
    return jsonify(inventory_list_schema.dump(parts)), 200

@inventory_bp.route("/", methods=["POST"])
@mechanic_token_required
@limiter.limit("5 per minute")
def add_part(mechanic_id):
    """
    Add a new inventory part
    ---
    tags:
      - Inventory
    summary: Add a new part to the inventory
    description: Mechanic-only route to add a new inventory item.
    security:
      - ApiKeyAuth: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - price
          properties:
            name:
              type: string
              example: Spark Plug
            price:
              type: number
              format: float
              example: 15.99
    responses:
      201:
        description: Part added successfully
        schema:
          $ref: '#/definitions/Inventory'
      400:
        description: Missing name or price
    """
    data = request.get_json()
    name = data.get("name")
    price = data.get("price")

    if not name or price is None:
        return jsonify({"message": "Name and price required."}), 400

    new_part = Inventory(name=name, price=price)
    db.session.add(new_part)
    db.session.commit()

    return inventory_schema.jsonify(new_part), 201

@inventory_bp.route("/<int:item_id>", methods=["PUT"])
@mechanic_token_required
def update_part(mechanic_id, item_id):
    """
    Update an inventory item
    ---
    tags:
      - Inventory
    summary: Update an existing part
    description: Mechanic-only route to update the name or price of a part.
    security:
      - ApiKeyAuth: []
    parameters:
      - name: item_id
        in: path
        type: integer
        required: true
        description: ID of the inventory item
      - in: body
        name: body
        schema:
          type: object
          properties:
            name:
              type: string
              example: Brake Pad
            price:
              type: number
              format: float
              example: 49.99
    responses:
      200:
        description: Part updated
        schema:
          $ref: '#/definitions/Inventory'
    """
    part = Inventory.query.get_or_404(item_id)
    data = request.get_json()

    part.name = data.get("name", part.name)
    part.price = data.get("price", part.price)

    db.session.commit()
    return inventory_schema.jsonify(part), 200

@inventory_bp.route("/<int:item_id>", methods=["DELETE"])
@mechanic_token_required
def delete_part(mechanic_id, item_id):
    """
    Delete an inventory part
    ---
    tags:
      - Inventory
    summary: Remove a part from the inventory
    description: Mechanic-only route to delete a part.
    security:
      - ApiKeyAuth: []
    parameters:
      - name: item_id
        in: path
        type: integer
        required: true
        description: ID of the inventory item
    responses:
      200:
        description: Part deleted
    """
    part = Inventory.query.get_or_404(item_id)
    db.session.delete(part)
    db.session.commit()
    return jsonify({"message": "Part deleted."}), 200

@inventory_bp.route("/add-part/<int:ticket_id>", methods=["POST"])
@mechanic_token_required
def add_part_to_ticket(mechanic_id, ticket_id):
    """
    Add a part to a service ticket
    ---
    tags:
      - Inventory
    summary: Attach a part to a service ticket
    description: Mechanic-only route to associate a part with a ticket.
    security:
      - ApiKeyAuth: []
    parameters:
      - name: ticket_id
        in: path
        type: integer
        required: true
        description: ID of the service ticket
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - part_id
          properties:
            part_id:
              type: integer
              example: 3
    responses:
      200:
        description: Part added to ticket
      404:
        description: Invalid ticket or part ID
    """
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    data = request.get_json()
    part_id = data.get("part_id")

    part = Inventory.query.get(part_id)
    if not part:
        return jsonify({"message": "Invalid part ID."}), 404

    if part not in ticket.parts:
        ticket.parts.append(part)
        db.session.commit()

    return jsonify({"message": "Part added to ticket."}), 200
