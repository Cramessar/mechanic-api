# File: application/blueprints/mechanics/routes.py

from flask import Blueprint, request, jsonify
from application.extensions import db
from application.models import Mechanic, ServiceTicket
from application.utils import hash_password, verify_password, encode_token, mechanic_token_required
from .schemas import mechanics_schema
from sqlalchemy import func

mechanics_bp = Blueprint("mechanics", __name__)

@mechanics_bp.route("/register", methods=["POST"])
def register_mechanic():
    """
    Register a new mechanic
    ---
    tags:
      - Mechanics
    summary: Register mechanic
    description: Register a new mechanic and return confirmation.
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - name
            - password
          properties:
            name:
              type: string
              example: Mike
            password:
              type: string
              example: strongpassword123
    responses:
      201:
        description: Mechanic registered successfully
      400:
        description: Missing name or password
      409:
        description: Mechanic already exists
    """
    data = request.get_json()
    name = data.get("name")
    password = data.get("password")

    if not name or not password:
        return jsonify({"message": "Name and password are required."}), 400

    if Mechanic.query.filter_by(name=name).first():
        return jsonify({"message": "Mechanic already exists."}), 409

    new_mechanic = Mechanic(name=name, password=hash_password(password))
    db.session.add(new_mechanic)
    db.session.commit()
    return jsonify({"message": "Mechanic registered successfully!"}), 201

@mechanics_bp.route("/login", methods=["POST"])
def login_mechanic():
    """
    Mechanic login
    ---
    tags:
      - Mechanics
    summary: Login mechanic and return JWT
    description: Mechanic login route. Returns JWT token upon successful authentication.
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - name
            - password
          properties:
            name:
              type: string
              example: Mike
            password:
              type: string
              example: strongpassword123
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            token:
              type: string
      401:
        description: Invalid credentials
    """
    data = request.get_json()
    name = data.get("name")
    password = data.get("password")

    mechanic = Mechanic.query.filter_by(name=name).first()
    if not mechanic or not verify_password(password, mechanic.password):
        return jsonify({"message": "Invalid credentials."}), 401

    token = encode_token(mechanic.id, role="mechanic")
    return jsonify({"token": token}), 200

@mechanics_bp.route("/protected", methods=["GET"])
@mechanic_token_required
def protected_mechanic_route(mechanic_id):
    """
    Protected route for mechanics
    ---
    tags:
      - Mechanics
    summary: Verify mechanic token
    description: Verifies token for mechanic role.
    security:
      - ApiKeyAuth: []
    responses:
      200:
        description: Authenticated
        schema:
          type: object
          properties:
            message:
              type: string
              example: Hello, mechanic #1! You're cleared for repairs.
    """
    return jsonify({"message": f"Hello, mechanic #{mechanic_id}! You're cleared for repairs."}), 200

@mechanics_bp.route("/by-tickets", methods=["GET"])
def get_mechanics_by_tickets():
    """
    Get mechanics ranked by ticket count
    ---
    tags:
      - Mechanics
    summary: Get top mechanics by tickets handled
    description: Returns a list of mechanics sorted by how many tickets they’ve worked on.
    responses:
      200:
        description: Mechanics with ticket counts
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              name:
                type: string
              ticket_count:
                type: integer
    """
    results = (
        db.session.query(
            Mechanic.id,
            Mechanic.name,
            func.count(ServiceTicket.id).label("ticket_count")
        )
        .join(Mechanic.tickets)
        .group_by(Mechanic.id)
        .order_by(func.count(ServiceTicket.id).desc())
        .all()
    )

    return jsonify([
        {"id": r[0], "name": r[1], "ticket_count": r[2]} for r in results
    ]), 200

@mechanics_bp.route("/", methods=["GET"])
def list_all_mechanics():
    """
    List all mechanics
    ---
    tags:
      - Mechanics
    summary: Get all registered mechanics
    description: Returns a list of all mechanics.
    responses:
      200:
        description: List of mechanics
        schema:
          type: array
          items:
            $ref: '#/definitions/Mechanic'
    """
    mechanics = Mechanic.query.all()
    return mechanics_schema.jsonify(mechanics), 200

mechanic_bp = mechanics_bp
