from flask import current_app, jsonify, url_for
from . import db, login_manager, pagedown
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
from markdown import markdown
import bleach


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Follows(db.Model):
    __tablename__ = 'follows'

    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)  # 用户是否邮件确认
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    # 用户资料字段
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    registration_time = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    # 对文章添加关系
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    # 关注关系添加联结
    followed = db.relationship('Follows',
                               foreign_keys=[Follows.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follows',
                                foreign_keys=[Follows.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    # 评论关系
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

        if self.role_id is None:
            if self.email == current_app.config.get('MAIL_USERNAME'):
                self.role = Role.query.filter_by(permissions=0xff).first()
                self.role_id = self.role.id
            else:
                self.role = Role.query.filter_by(default=True).first()
                self.role_id = self.role.id

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
        """生成邮件确认token"""
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

    def ping(self):
        """last_seen字段更新时间"""
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def is_following(self, user):
        """
        验证是否是已经关注的用户
        :param user: 待验证用户
        :return: True or False
        """
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        """
        验证是否被user关注
        :param user: 待验证用户
        :return: True or False
        """
        return self.followers.filter_by(follower_id=user.id).first() is not None

    def follow(self, user):
        """
        关注
        :param user: 要关注对象
        :return:
        """
        if not self.is_following(user):
            f = Follows(followed=user, follower=self)
            db.session.add(f)
            db.session.commit()

    def unfollow(self, user):
        """
        取消关注
        :param user: 取消关注的对象
        :return:
        """
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)
            db.session.commit()

    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.load(token)
        except:
            return None
        return User.query.filter_by(id=data['id'])

    def to_json(self):
        """用户资源转化为json格式"""
        jsonify({
            'url': url_for('api.get_post', id=self.id, _external=True),
        })

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


class Post(db.Model):
    """博客文章数据库模型"""
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), index=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    @staticmethod
    def change_body_to_html(target, value, oldvalue, initiator):
        allow_tag = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                     'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                     'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(markdown(value, output_format='html'), tags=allow_tag, strip=True))

    def to_json(self):
        json_post = jsonify({
            'url': url_for('api.get_post', id=self.id, _external=True),
            'title': self.title,
            'body': self.body,
            'timestamp': self.timestamp,
            'author': url_for('api.get_user', id=self.author_id, _external=True),
            'comments': url_for('api.get_comments', id=self.id, _external=True),
            'comment_count': self.comments.count()
        })
        return json_post


# 利用sqlalchemy的event监听POST的body字段,如果设置新值则触发函数
db.event.listen(Post.body, 'set', Post.change_body_to_html)


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    disable = db.Column(db.Boolean, default=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    @staticmethod
    def change_body_to_html(target, value, oldvalue, initiator):
        allow_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i', 'strong']
        target.body_html = bleach.linkify(bleach.clean(markdown(value, output_format='html'), tags=allow_tags, strip=True))


db.event.listen(Comment.body, 'set', Comment.change_body_to_html)