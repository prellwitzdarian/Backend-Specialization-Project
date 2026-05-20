from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Inventory, db
from app.extensions import limiter
from app.utils.util import mechanic_required
from .schemas import inventory_schema, inventories_schema
from . import inventory_bp


@inventory_bp.route('/', methods=['POST'])
@limiter.limit('20 per hour')
@mechanic_required
def create_inventory_part(mechanic_id):
    try:
        inventory_data = inventory_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Inventory).where(Inventory.name == inventory_data['name'])
    existing_part = db.session.execute(query).scalars().first()
    if existing_part:
        return jsonify({'error': 'Inventory part already exists.'}), 400

    new_part = Inventory(**inventory_data)
    db.session.add(new_part)
    db.session.commit()
    return jsonify(inventory_schema.dump(new_part)), 201


@inventory_bp.route('/', methods=['GET'])
def get_inventory():
    query = select(Inventory)
    inventory_parts = db.session.execute(query).scalars().all()
    return jsonify(inventories_schema.dump(inventory_parts)), 200


@inventory_bp.route('/<int:inventory_id>', methods=['GET'])
def get_inventory_item(inventory_id):
    part = db.session.get(Inventory, inventory_id)
    if not part:
        return jsonify({'error': 'Inventory part not found.'}), 404
    return jsonify(inventory_schema.dump(part)), 200


@inventory_bp.route('/<int:inventory_id>', methods=['PUT'])
@mechanic_required
def update_inventory_part(mechanic_id, inventory_id):
    part = db.session.get(Inventory, inventory_id)
    if not part:
        return jsonify({'error': 'Inventory part not found.'}), 404

    try:
        inventory_data = inventory_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    if 'name' in inventory_data and inventory_data['name'] != part.name:
        existing_part = db.session.execute(
            select(Inventory).where(Inventory.name == inventory_data['name'])
        ).scalars().first()
        if existing_part:
            return jsonify({'error': 'Inventory part already exists.'}), 400

    for key, value in inventory_data.items():
        setattr(part, key, value)

    db.session.commit()
    return jsonify(inventory_schema.dump(part)), 200


@inventory_bp.route('/<int:inventory_id>', methods=['DELETE'])
@mechanic_required
def delete_inventory_part(mechanic_id, inventory_id):
    part = db.session.get(Inventory, inventory_id)
    if not part:
        return jsonify({'error': 'Inventory part not found.'}), 404

    db.session.delete(part)
    db.session.commit()
    return jsonify({'message': f'Inventory part {inventory_id} deleted successfully.'}), 200
