# File: application/blueprints/customers/routes.py

from flask import Blueprint, request, jsonify
from application.models import db, Customer, ServiceTicket
from application.utils import encode_token, token_required, hash_password, verify_password
from application.extensions import limiter
from sqlalchemy.exc import IntegrityError
from .schemas import customer_schema, customers_schema, login_schema

customers_bp = Blueprint("customers", __name__)

@customers_bp.route("/register", methods=["POST"])
def register_customer():
    """
    Register a new customer
    ---
    tags:
      - Customers
    summary: Register customer
    description: Creates a new customer and returns their info.
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - email
            - password
          properties:
            name:
              type: string
              example: Alice
            email:
              type: string
              example: alice@example.com
            password:
              type: string
              example: securepassword123
    responses:
      201:
        description: Customer created successfully
        schema:
          type: object
          properties:
            id:
              type: integer
            name:
              type: string
            email:
              type: string
      400:
        description: Missing field
      409:
        description: Email already registered
    """
    data = request.get_json()
    try:
        new_customer = Customer(
            name=data["name"],
            email=data["email"],
            password=hash_password(data["password"])
        )
        db.session.add(new_customer)
        db.session.commit()
        return customer_schema.jsonify(new_customer), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Email already registered."}), 409
    except KeyError as e:
        return jsonify({"error": f"Missing field: {e}"}), 400


@customers_bp.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login_customer():
    """
    Customer Login
    ---
    tags:
      - Customers
    summary: Login as a customer
    description: Authenticates a customer and returns a JWT token.
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: alice@example.com
            password:
              type: string
              example: securepassword123
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            token:
              type: string
      400:
        description: Validation error
      401:
        description: Invalid credentials
    """
    data = request.get_json()
    errors = login_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    customer = Customer.query.filter_by(email=data["email"]).first()
    if not customer or not verify_password(data["password"], customer.password):
        return jsonify({"message": "Invalid credentials"}), 401

    token = encode_token(customer.id, role="customer")
    return jsonify({"token": token})


@customers_bp.route("/<string:username>/tickets", methods=["GET"])
@token_required
def get_customer_tickets(customer_id, username):
    """
    Get a customer's service tickets
    ---
    tags:
      - Customers
    summary: Get tickets for a specific customer
    description: Returns a list of tickets for a customer (must be authenticated).
    security:
      - ApiKeyAuth: []
    parameters:
      - name: username
        in: path
        type: string
        required: true
        description: The username of the customer
    responses:
      200:
        description: List of tickets
      403:
        description: Unauthorized or customer not found
    """
    customer = Customer.query.filter_by(name=username).first()
    if not customer or customer.id != customer_id:
        return jsonify({"message": "Unauthorized or customer not found."}), 403

    tickets = ServiceTicket.query.filter_by(customer_id=customer.id).all()
    return jsonify([
        {
            "id": t.id,
            "description": t.description,
            "status": t.status
        } for t in tickets
    ])


@customers_bp.route("/", methods=["GET"])
def get_all_customers():
    """
    Get all customers (paginated)
    ---
    tags:
      - Customers
    summary: List all customers
    description: Returns a paginated list of customers.
    parameters:
      - name: page
        in: query
        type: integer
        required: false
        default: 1
      - name: per_page
        in: query
        type: integer
        required: false
        default: 10
    responses:
      200:
        description: Paginated customer list
    """
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    customers = Customer.query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "customers": customers_schema.dump(customers.items),
        "total": customers.total,
        "pages": customers.pages,
        "current_page": customers.page
    })

@customers_bp.route("/<int:customer_id>", methods=["DELETE"])
@token_required
def delete_customer(authenticated_customer_id, customer_id):
    """
    Delete a customer account
    ---
    tags:
      - Customers
    summary: Delete a customer
    description: Deletes the customer with the given ID. The authenticated customer must match the customer being deleted.
    security:
      - ApiKeyAuth: []
    parameters:
      - name: customer_id
        in: path
        required: true
        type: integer
        description: The ID of the customer to delete
    responses:
      200:
        description: Customer deleted successfully
      403:
        description: Forbidden – cannot delete another user's account
      404:
        description: Customer not found
    """
    if authenticated_customer_id != customer_id:
        return jsonify({"message": "You are not authorized to delete this account."}), 403

    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({"message": "Customer not found."}), 404

    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": "Customer deleted successfully."}), 200
