from jose import jwt
from datetime import datetime, timezone, timedelta
from functools import wraps
from flask import request, jsonify

SECRET_KEY = 'super secret secrets'


def encode_token(user_id, role='customer'):
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(hours=1),
        'iat': datetime.now(timezone.utc),
        'sub': str(user_id),
        'role': role,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


def encode_mechanic_token(mechanic_id):
    return encode_token(mechanic_id, role='mechanic')


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization') or request.environ.get('HTTP_AUTHORIZATION') or ''
        token = None
        if auth_header:
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ', 1)[1]
            else:
                # accept bare token as well
                token = auth_header.strip()

        if not token:
            return jsonify({'message': 'Missing authorization token'}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            sub = data.get('sub')
            try:
                # convert numeric subject to int for route comparisons
                if isinstance(sub, str) and sub.isdigit():
                    sub = int(sub)
            except Exception:
                pass
            return f(sub, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired'}), 401
        except Exception:
            return jsonify({'message': 'Invalid token'}), 401

    return decorated


def mechanic_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization') or request.environ.get('HTTP_AUTHORIZATION') or ''
        token = None
        if auth_header:
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ', 1)[1]
            else:
                token = auth_header.strip()

        if not token:
            return jsonify({'message': 'Missing authorization token'}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            if data.get('role') != 'mechanic':
                return jsonify({'message': 'Mechanic authorization required'}), 403
            sub = data.get('sub')
            try:
                if isinstance(sub, str) and sub.isdigit():
                    sub = int(sub)
            except Exception:
                pass
            return f(sub, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired'}), 401
        except Exception:
            return jsonify({'message': 'Invalid token'}), 401

    return decorated 