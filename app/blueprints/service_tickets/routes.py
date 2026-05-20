from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Service_tickets, Mechanics, Inventory, db
from app.extensions import limiter
from app.utils.util import token_required, mechanic_required
from .schemas import (
    service_ticket_schema,
    service_tickets_schema,
    edit_service_ticket_schema,
)
from . import service_tickets_bp


@service_tickets_bp.route('/', methods=['POST'])
@limiter.limit('20 per hour')
@token_required
def create_service_ticket(customer_id):
    try:
        ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    ticket_data['customer_id'] = customer_id
    new_ticket = Service_tickets(**ticket_data)
    db.session.add(new_ticket)
    db.session.commit()
    return jsonify(service_ticket_schema.dump(new_ticket)), 201


@service_tickets_bp.route('/', methods=['GET'])
@limiter.limit('100 per hour')
def get_service_tickets():
    query = select(Service_tickets)
    tickets = db.session.execute(query).scalars().all()
    return jsonify(service_tickets_schema.dump(tickets)), 200


@service_tickets_bp.route('/<int:ticket_id>', methods=['GET'])
def get_service_ticket(ticket_id):
    ticket = db.session.get(Service_tickets, ticket_id)
    if not ticket:
        return jsonify({'error': 'Service ticket not found.'}), 404
    return jsonify(service_ticket_schema.dump(ticket)), 200


@service_tickets_bp.route('/<int:ticket_id>/assign-mechanic/<int:mechanic_id>', methods=['PUT'])
@mechanic_required
def assign_mechanic(token_mechanic_id, ticket_id, mechanic_id):
    ticket = db.session.get(Service_tickets, ticket_id)
    mechanic = db.session.get(Mechanics, mechanic_id)

    if not ticket or not mechanic:
        return jsonify({'error': 'Ticket or mechanic not found.'}), 404

    if mechanic not in ticket.mechanics:
        ticket.mechanics.append(mechanic)
        db.session.commit()

    return jsonify(service_ticket_schema.dump(ticket)), 200


@service_tickets_bp.route('/<int:ticket_id>/remove-mechanic/<int:mechanic_id>', methods=['PUT'])
@mechanic_required
def remove_mechanic(token_mechanic_id, ticket_id, mechanic_id):
    ticket = db.session.get(Service_tickets, ticket_id)
    mechanic = db.session.get(Mechanics, mechanic_id)

    if not ticket or not mechanic:
        return jsonify({'error': 'Ticket or mechanic not found.'}), 404

    if mechanic in ticket.mechanics:
        ticket.mechanics.remove(mechanic)
        db.session.commit()

    return jsonify(service_ticket_schema.dump(ticket)), 200


@service_tickets_bp.route('/<int:ticket_id>/edit', methods=['PUT'])
@mechanic_required
def edit_service_ticket(mechanic_id, ticket_id):
    ticket = db.session.get(Service_tickets, ticket_id)
    if not ticket:
        return jsonify({'error': 'Service ticket not found.'}), 404

    try:
        edits = edit_service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for mechanic_id_to_add in edits.get('add_mechanic_ids', []):
        mechanic = db.session.get(Mechanics, mechanic_id_to_add)
        if mechanic and mechanic not in ticket.mechanics:
            ticket.mechanics.append(mechanic)

    for mechanic_id_to_remove in edits.get('remove_mechanic_ids', []):
        mechanic = db.session.get(Mechanics, mechanic_id_to_remove)
        if mechanic and mechanic in ticket.mechanics:
            ticket.mechanics.remove(mechanic)

    db.session.commit()
    return jsonify(service_ticket_schema.dump(ticket)), 200


@service_tickets_bp.route('/<int:ticket_id>/add-part/<int:inventory_id>', methods=['PUT'])
@mechanic_required
def add_part_to_ticket(mechanic_id, ticket_id, inventory_id):
    ticket = db.session.get(Service_tickets, ticket_id)
    inventory = db.session.get(Inventory, inventory_id)

    if not ticket or not inventory:
        return jsonify({'error': 'Ticket or inventory part not found.'}), 404

    if inventory not in ticket.parts:
        ticket.parts.append(inventory)
        db.session.commit()

    return jsonify(service_ticket_schema.dump(ticket)), 200
