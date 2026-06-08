import time
from functools import wraps
from flask import jsonify


SUCCESS = 0
FAIL = 1
ERROR = 2

PARAM_ERROR = 400
UNAUTHORIZED = 401
FORBIDDEN = 403
NOT_FOUND = 404
INTERNAL_ERROR = 500


class AppError(Exception):
    def __init__(self, message, code=FAIL, data=None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.data = data


def success(data=None, message='success'):
    return jsonify({
        'code': SUCCESS,
        'message': message,
        'data': data,
        'timestamp': int(time.time() * 1000)
    })


def fail(message='fail', data=None, code=FAIL):
    return jsonify({
        'code': code,
        'message': message,
        'data': data,
        'timestamp': int(time.time() * 1000)
    })


def error(message='error', data=None, code=INTERNAL_ERROR):
    return jsonify({
        'code': code,
        'message': message,
        'data': data,
        'timestamp': int(time.time() * 1000)
    })


def handle_error(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except AppError as e:
            return fail(e.message, e.data, e.code)
        except Exception as e:
            return error(str(e))
    return wrapper
