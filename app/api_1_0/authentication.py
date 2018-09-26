from flask.ext.httpauth import HTTPBasicAuth
from ..models import AnonymousUser, User
from .errors import unauthorized, forbidden
from . import api
from flask import jsonify

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email_or_token, password):
    """验证邮箱密码回调函数"""
    if email_or_token == '':
        g.current_user = AnonymousUser()
        return True
    if not password:
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.token_used = False
    g.current_user = user
    return user.verify_password(password)


@auth.error_handler
def auth_error():
    """验证错误函数"""
    return unauthorized('Invalid Credentials')


@api.before_request
@auth.login_required
def befor_request():
    """请求前验证,如果已登录,并且没有邮箱验证,报403错误"""
    if not g.current_user.is_anonymous and not g.current_user.confirmed:
        return forbidden('Unconfirmed Account')


@api.route('/token')
def get_token():
    """生成用户token"""
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credintials')
    return jsonify({'token': g.current_user.generate_auth_token(expiration=60*60),
            'expiration': 60*60})


