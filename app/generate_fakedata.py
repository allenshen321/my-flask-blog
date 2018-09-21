from .models import User, Post
from sqlalchemy.exc import IntegrityError
from . import db
from random import seed, randint
import forgery_py


def generate_user_fake(count=100):
    seed()
    for i in range(count):
        user = User()
        user.email = forgery_py.internet.email_address()
        user.username = forgery_py.internet.user_name(True)
        user.confirmed = True
        user.name = forgery_py.name.full_name()
        user.location = forgery_py.address.city()
        user.about_me = forgery_py.lorem_ipsum.sentence()
        user.last_seen = forgery_py.date.date(True)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def generate_post_fake(count=100):
    seed()
    user_count = User.query.count()
    for i in range(count):
        post = Post()
        post.title = forgery_py.lorem_ipsum.title()
        post.body = forgery_py.lorem_ipsum.paragraphs()
        post.author = User.query.offset(randint(0, user_count-1)).first()
        db.session.add(post)
        db.session.commit()
