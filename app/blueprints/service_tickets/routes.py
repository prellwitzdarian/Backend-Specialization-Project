from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Service_tickets, Mechanics, db
from .schemas import service_ticket_schema, service_tickets_schema
from . import service_tickets_bp

@service_tickets_bp.route('/', methods=['POST'])
def create_service_ticket():
    try:
        ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_ticket = Service_tickets(**ticket_data)
    db.session.add(new_ticket)
    db.session.commit()
    return service_ticket_schema.jsonify(new_ticket), 201

@service_tickets_bp.route('/', methods=['GET'])
def get_service_tickets():
    query = select(Service_tickets)
    tickets = db.session.execute(query).scalars().all()
    return service_tickets_schema.jsonify(tickets), 200

@service_tickets_bp.route('/<int:ticket_id>/assign-mechanic/<int:mechanic_id>', methods=['PUT'])
def assign_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(Service_tickets, ticket_id)
    mechanic = db.session.get(Mechanics, mechanic_id)

    if not ticket or not mechanic:
        return jsonify({"error": "Ticket or mechanic not found."}), 404

    if mechanic not in ticket.mechanics:
        ticket.mechanics.append(mechanic)
        db.session.commit()

    return service_ticket_schema.jsonify(ticket), 200

@service_tickets_bp.route('/<int:ticket_id>/remove-mechanic/<int:mechanic_id>', methods=['PUT'])
def remove_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(Service_tickets, ticket_id)
    mechanic = db.session.get(Mechanics, mechanic_id)

    if not ticket or not mechanic:
        return jsonify({"error": "Ticket or mechanic not found."}), 404

    if mechanic in ticket.mechanics:
        ticket.mechanics.remove(mechanic)
        db.session.commit()

    return service_ticket_schema.jsonify(ticket), 200
