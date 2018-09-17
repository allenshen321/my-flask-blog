from flask import current_app
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin, AnonymousUserMixin
from . import login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)  # 用户是否邮件确认
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

        if self.role is None:
            if self.email == current_app.config.get('FLASKY_ADMIN'):
                self.role = Role.query.filter_by(permissions=0xff).first()
            else:
                self.role = Role.query.filter_by(default=True).first()

    @property
    def password(self):
        """设置密码为只读属性"""
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        """密码加密"""
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)

    def can(self, permissions):
        """验证权限"""
        return self.role is not None and (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        """验证是否是管理员"""
        return self.can(Permission.ADMINISTER)

    def generate_confirmation_token(self, expiration=3600):
        """生成确认token"""
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        """验证确认token"""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    def __repr__(self):
        return '<User %s>' % self.username


class AnonymousUser(AnonymousUserMixin):
    """定义未登录用户权限验证的类"""
    def can(self, permissions):
        """权限验证"""
        return False

    def is_administrator(self):
        return False


# 设置未登录用户的current_user的值
login_manager.anonymous_user = AnonymousUser


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    default = db.Column(db.Boolean, index=True)
    permissions = db.Column(db.Integer, index=True)
    users = db.relationship('User', backref='role')

    def __repr__(self):
        return '<Role %s>' % self.name

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS,
                          False),
            'Administrator': (0xff, False)
        }

        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if not role:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()


class Permission:
    FOLLOW = 0X01
    COMMENT = 0X02
    WRITE_ARTICLES = 0X04
    MODERATE_COMMENTS = 0X08
    ADMINISTER = 0X80
