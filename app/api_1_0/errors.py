from flask import jsonify


def forbidden(message):
    """403错误,辅助函数"""
    response = jsonify({'error': 'forbidden',
                        'message': message})
    response.status_code = 403
    return response


def unauthorized(message):
    """401未授权错误函数"""
    response = jsonify({'error': 'unauthorized',
                        'message': message})
    response.status_code = 401
    return response
