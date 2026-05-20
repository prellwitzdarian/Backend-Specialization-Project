from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Mechanics, db
from app.extensions import limiter
from app.utils.util import encode_mechanic_token, mechanic_required
from .schemas import (
    mechanic_schema,
    mechanics_schema,
    mechanic_load_schema,
    mechanic_login_schema,
)
from . import mechanics_bp


@mechanics_bp.route('/login', methods=['POST'])
@limiter.limit('10 per minute')
def login():
    try:
        credentials = mechanic_login_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Mechanics).where(Mechanics.email == credentials['email'])
    mechanic = db.session.execute(query).scalars().first()

    if mechanic and mechanic.password == credentials['password']:
        token = encode_mechanic_token(mechanic.id)
        return jsonify({'status': 'success', 'token': token}), 200

    return jsonify({'message': 'Invalid email or password.'}), 401


@mechanics_bp.route('/', methods=['POST'])
@limiter.limit('10 per hour')
def create_mechanic():
    try:
        mechanic_data = mechanic_load_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Mechanics).where(Mechanics.email == mechanic_data['email'])
    existing_mechanic = db.session.execute(query).scalars().first()
    if existing_mechanic:
        return jsonify({'error': 'Email already exists.'}), 400

    new_mechanic = Mechanics(**mechanic_data)
    db.session.add(new_mechanic)
    db.session.commit()

    return jsonify(mechanic_schema.dump(new_mechanic)), 201


@mechanics_bp.route('/', methods=['GET'])
def get_mechanics():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    query = select(Mechanics)
    pagination = db.paginate(query, page=page, per_page=per_page)
    mechanics = pagination.items

    return jsonify({
        'mechanics': mechanics_schema.dump(mechanics),
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages,
    }), 200


@mechanics_bp.route('/<int:mechanic_id>', methods=['PUT'])
@mechanic_required
def update_mechanic(token_mechanic_id, mechanic_id):
    if token_mechanic_id != mechanic_id:
        return jsonify({'error': 'Unauthorized'}), 403

    mechanic = db.session.get(Mechanics, mechanic_id)
    if not mechanic:
        return jsonify({'error': 'Mechanic not found.'}), 404

    try:
        mechanic_data = mechanic_load_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    if 'email' in mechanic_data and mechanic_data['email'] != mechanic.email:
        existing_mechanic = db.session.execute(
            select(Mechanics).where(Mechanics.email == mechanic_data['email'])
        ).scalars().first()
        if existing_mechanic:
            return jsonify({'error': 'Email already exists.'}), 400

    for key, value in mechanic_data.items():
        setattr(mechanic, key, value)

    db.session.commit()
    return jsonify(mechanic_schema.dump(mechanic)), 200


@mechanics_bp.route('/<int:mechanic_id>', methods=['DELETE'])
@mechanic_required
def delete_mechanic(token_mechanic_id, mechanic_id):
    if token_mechanic_id != mechanic_id:
        return jsonify({'error': 'Unauthorized'}), 403

    mechanic = db.session.get(Mechanics, mechanic_id)
    if not mechanic:
        return jsonify({'error': 'Mechanic not found.'}), 404

    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({'message': f'Mechanic {mechanic_id} deleted successfully.'}), 200


@mechanics_bp.route('/popular', methods=['GET'])
def popular_mechanics():
    mechanics = db.session.execute(select(Mechanics)).scalars().all()
    mechanics.sort(key=lambda mechanic: len(mechanic.service_tickets), reverse=True)
    return jsonify(mechanics_schema.dump(mechanics)), 200


@mechanics_bp.route('/search', methods=['GET'])
def search_mechanic():
    name = request.args.get('name', '')
    query = select(Mechanics).where(Mechanics.name.ilike(f'%{name}%'))
    mechanics = db.session.execute(query).scalars().all()
    return jsonify(mechanics_schema.dump(mechanics)), 200
    
    
    

