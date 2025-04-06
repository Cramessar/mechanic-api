# File: "application/blueprints/service_tickets/routes.py"

from flask import Blueprint, request, jsonify
from application.extensions import db, limiter
from application.models import ServiceTicket, Mechanic, Inventory
from application.utils import token_required, mechanic_token_required
from .schemas import ticket_schema, tickets_schema

service_tickets_bp = Blueprint("service_tickets", __name__)

@service_tickets_bp.route("/", methods=["GET"])
def list_all_tickets():
    """
    List all service tickets
    ---
    tags:
      - Service Tickets
    summary: Retrieve all tickets
    description: Returns a full list of all service tickets (admin/demo use).
    responses:
      200:
        description: A list of service tickets
        schema:
          type: array
          items:
            $ref: '#/definitions/ServiceTicket'
    """
    tickets = ServiceTicket.query.all()
    return tickets_schema.jsonify(tickets), 200

@service_tickets_bp.route("/", methods=["POST"])
@token_required
def create_ticket(customer_id):
    """
    Create a new service ticket (auth: customer)
    ---
    tags:
      - Service Tickets
    summary: Create ticket
    description: Create a service ticket for the authenticated customer.
    security:
      - ApiKeyAuth: []
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - description
          properties:
            description:
              type: string
              example: Car making grinding noise when braking
    responses:
      201:
        description: Ticket created successfully
      400:
        description: Description is required
    """
    data = request.get_json()
    description = data.get("description")

    if not description:
        return jsonify({"message": "Description is required."}), 400

    ticket = ServiceTicket(description=description, customer_id=customer_id)
    db.session.add(ticket)
    db.session.commit()

    return jsonify({"message": "Ticket created", "ticket_id": ticket.id}), 201

@service_tickets_bp.route("/my-tickets", methods=["GET"])
@token_required
@limiter.limit("5 per minute")
def get_my_tickets(customer_id):
    """
    Get all tickets for the logged-in customer
    ---
    tags:
      - Service Tickets
    summary: View my tickets
    description: Returns all tickets for the current authenticated customer.
    security:
      - ApiKeyAuth: []
    responses:
      200:
        description: List of tickets for customer
    """
    tickets = ServiceTicket.query.filter_by(customer_id=customer_id).all()
    return tickets_schema.jsonify(tickets), 200

@service_tickets_bp.route("/<int:ticket_id>/edit", methods=["PUT"])
@token_required
def edit_mechanics_on_ticket(customer_id, ticket_id):
    """
    Add or remove mechanics from a ticket
    ---
    tags:
      - Service Tickets
    summary: Edit assigned mechanics
    description: Allows the ticket owner to add or remove mechanics assigned to a service ticket.
    security:
      - ApiKeyAuth: []
    parameters:
      - name: ticket_id
        in: path
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            add_ids:
              type: array
              items:
                type: integer
              example: [1, 2]
            remove_ids:
              type: array
              items:
                type: integer
              example: [3]
    responses:
      200:
        description: Mechanics updated
      404:
        description: Ticket not found or unauthorized
    """
    ticket = ServiceTicket.query.filter_by(id=ticket_id, customer_id=customer_id).first()
    if not ticket:
        return jsonify({"message": "Ticket not found or unauthorized"}), 404

    data = request.get_json()
    add_ids = data.get("add_ids", [])
    remove_ids = data.get("remove_ids", [])
    added, removed = [], []

    for mid in add_ids:
        mech = Mechanic.query.get(mid)
        if mech and mech not in ticket.mechanics:
            ticket.mechanics.append(mech)
            added.append(mid)

    for mid in remove_ids:
        mech = Mechanic.query.get(mid)
        if mech and mech in ticket.mechanics:
            ticket.mechanics.remove(mech)
            removed.append(mid)

    db.session.commit()
    return jsonify({"message": "Mechanics updated", "added": added, "removed": removed}), 200

@service_tickets_bp.route("/<int:ticket_id>/add-part", methods=["PUT"])
@token_required
def add_parts_to_ticket(customer_id, ticket_id):
    """
    Add parts to a ticket (auth: customer)
    ---
    tags:
      - Service Tickets
    summary: Add parts
    description: Add inventory parts to a customer’s ticket.
    security:
      - ApiKeyAuth: []
    parameters:
      - name: ticket_id
        in: path
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            part_ids:
              type: array
              items:
                type: integer
              example: [1, 4]
    responses:
      200:
        description: Parts added to ticket
      404:
        description: Ticket not found or unauthorized
    """
    ticket = ServiceTicket.query.filter_by(id=ticket_id, customer_id=customer_id).first()
    if not ticket:
        return jsonify({"message": "Ticket not found or unauthorized"}), 404

    part_ids = request.get_json().get("part_ids", [])

    for pid in part_ids:
        part = Inventory.query.get(pid)
        if part and part not in ticket.parts:
            ticket.parts.append(part)

    db.session.commit()
    return jsonify({"message": "Parts added to ticket"}), 200

@service_tickets_bp.route("/<int:ticket_id>/update-status", methods=["PUT"])
@mechanic_token_required
def update_ticket_status(mechanic_id, ticket_id):
    """
    Update ticket status (auth: mechanic)
    ---
    tags:
      - Service Tickets
    summary: Update status
    description: Allows a mechanic to update the status of a service ticket.
    security:
      - ApiKeyAuth: []
    parameters:
      - name: ticket_id
        in: path
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
          required:
            - status
          properties:
            status:
              type: string
              example: Completed
    responses:
      200:
        description: Status updated
      400:
        description: Status missing
      404:
        description: Ticket not found
    """
    ticket = ServiceTicket.query.get(ticket_id)
    if not ticket:
        return jsonify({"message": "Ticket not found"}), 404

    status = request.get_json().get("status")
    if not status:
        return jsonify({"message": "Status is required"}), 400

    ticket.status = status
    db.session.commit()
    return jsonify({"message": f"Status updated to '{status}'"}), 200

