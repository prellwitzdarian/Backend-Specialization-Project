from jose import jwt
from datetime import datetime, timezone, timedelta
from functools import wraps
from flask import request, jsonify

SECRET_KEY = 'super secret secrets'


def encode_token(user_id, role='customer'):
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(hours=1),
        'iat': datetime.now(timezone.utc),
        'sub': user_id,
        'role': role,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


def encode_mechanic_token(mechanic_id):
    return encode_token(mechanic_id, role='mechanic')


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.split()[1] if auth_header.startswith('Bearer ') else None

        if not token:
            return jsonify({'message': 'Missing authorization token'}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            return f(data['sub'], *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired'}), 401
        except jwt.JWTError:
            return jsonify({'message': 'Invalid token'}), 401

    return decorated


def mechanic_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.split()[1] if auth_header.startswith('Bearer ') else None

        if not token:
            return jsonify({'message': 'Missing authorization token'}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            if data.get('role') != 'mechanic':
                return jsonify({'message': 'Mechanic authorization required'}), 403
            return f(data['sub'], *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired'}), 401
        except jwt.JWTError:
            return jsonify({'message': 'Invalid token'}), 401

    return decorated 