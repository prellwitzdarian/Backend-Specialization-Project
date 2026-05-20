from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Customers, Service_tickets, db
from app.extensions import limiter, cache
from app.utils.util import encode_token, token_required
from .schemas import customer_schema, customers_schema, customer_load_schema, login_schema
from . import customers_bp
from app.blueprints.service_tickets.schemas import service_tickets_schema


@customers_bp.route('/login', methods=['POST'])
@limiter.limit('10 per minute')
def login():
    try:
        credentials = login_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Customers).where(Customers.email == credentials['email'])
    customer = db.session.execute(query).scalars().first()

    if customer and customer.password == credentials['password']:
        token = encode_token(customer.id)
        return jsonify({'status': 'success', 'token': token}), 200

    return jsonify({'message': 'Invalid email or password.'}), 401


@customers_bp.route('/', methods=['POST'])
@limiter.limit('10 per hour')
def create_customer():
    try:
        customer_data = customer_load_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Customers).where(Customers.email == customer_data['email'])
    existing_customer = db.session.execute(query).scalars().first()
    if existing_customer:
        return jsonify({'error': 'Email already associated with an account.'}), 400

    new_customer = Customers(**customer_data)
    db.session.add(new_customer)
    db.session.commit()
    return jsonify(customer_schema.dump(new_customer)), 201


@customers_bp.route('/', methods=['GET'])
@cache.cached(timeout=60, query_string=True)
def get_customers():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    query = select(Customers)
    pagination = db.paginate(query, page=page, per_page=per_page)
    customers = pagination.items

    return jsonify({
        'customers': customers_schema.dump(customers),
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages,
    }), 200


@customers_bp.route('/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    customer = db.session.get(Customers, customer_id)
    if customer:
        return jsonify(customer_schema.dump(customer)), 200
    return jsonify({'error': 'Customer not found.'}), 404


@customers_bp.route('/<int:customer_id>', methods=['PUT'])
@limiter.limit('10 per hour')
@token_required
def update_customer(token_customer_id, customer_id):
    if token_customer_id != customer_id:
        return jsonify({'error': 'Unauthorized'}), 403

    customer = db.session.get(Customers, customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found.'}), 404

    try:
        customer_data = customer_load_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    if 'email' in customer_data and customer_data['email'] != customer.email:
        existing_customer = db.session.execute(
            select(Customers).where(Customers.email == customer_data['email'])
        ).scalars().first()
        if existing_customer:
            return jsonify({'error': 'Email already associated with an account.'}), 400

    for key, value in customer_data.items():
        setattr(customer, key, value)

    db.session.commit()
    return jsonify(customer_schema.dump(customer)), 200


@customers_bp.route('/<int:customer_id>', methods=['DELETE'])
@limiter.limit('10 per hour')
@token_required
def delete_customer(token_customer_id, customer_id):
    if token_customer_id != customer_id:
        return jsonify({'error': 'Unauthorized'}), 403

    customer = db.session.get(Customers, customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found.'}), 404

    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message': f'Customer id: {customer_id} successfully deleted.'}), 200


@customers_bp.route('/my-tickets', methods=['GET'])
@token_required
def get_my_tickets(customer_id):
    query = select(Service_tickets).where(Service_tickets.customer_id == customer_id)
    tickets = db.session.execute(query).scalars().all()
    return jsonify(service_tickets_schema.dump(tickets)), 200

