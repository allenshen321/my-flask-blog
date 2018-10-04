import unittest
from app.models import User, Role, Permission, Post, Comment
from app import create_app, db


class UserModelTestCase(unittest.TestCase):
    """测试模型中User模型中,关于密码加密"""

    def setUp(self):
        self.app = create_app('test_config')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_set_user_role(self):
        u = User(email='test@example.com', password='cat')
        self.assertTrue(u.role_id)

    def test_password_setter(self):
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        u1 = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u1.password_hash != u2.password_hash)

    def test_roles_and_permissions(self):
        u = User(email='test@example.com', password='test')
        self.assertTrue(u.can(Permission.WRITE_ARTICLES))
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertTrue(u.can(Permission.FOLLOW))
        self.assertFalse(u.can(Permission.MODERATE_COMMENTS))
        self.assertFalse(u.can(Permission.ADMINISTER))

    def test_valid_confirmation_token(self):
        u = User(password='cat')
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))

    def test_invalid_confirmation_token(self):
        u1 = User(password='cat')
        u2 = User(password='dog')
        token = u1.generate_confirmation_token()
        self.assertFalse(u2.confirm(token))

    def test_is_following_and_followed(self):
        u1 = User(email='test@example.com', password='test')
        u2 = User(email='test3@example.com', password='test')
        print(u1, u2)
        # 测试关注功能
        u1.follow(u2)
        self.assertTrue(u1.is_following(u2))
        self.assertTrue(u2.is_followed_by(u1))
        # 测试取消关注
        u1.unfollow(u2)
        self.assertFalse(u1.is_following(u2))
        self.assertFalse(u2.is_followed_by(u1))
        # 测试增加自己为关注
        u1.add_self_follows()
        self.assertTrue(u1.is_following(u1))
        self.assertTrue(u1.is_followed_by(u1))

    def test_generate_and_verify_user_token(self):
        u = User(email='test@example.com', password='test', username='test')
        db.session.add(u)
        db.session.commit()
        token = u.generate_auth_token(3600)
        self.assertTrue(token)
        self.assertTrue(User.verify_auth_token(token))

    def test_post_change_body_to_html(self):
        post = Post(body='cat')
        db.session.add(post)
        db.session.commit()
        self.assertTrue(post.body_html)

    def test_comment_change_body_to_html(self):
        comment = Comment(body='ct')
        db.session.add(comment)
        db.session.commit()
        self.assertTrue(comment.body_html)







