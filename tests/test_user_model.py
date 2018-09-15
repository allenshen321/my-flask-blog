import unittest
from app.models import User, Role, Permission


class UserModelTestCase(unittest.TestCase):
    """测试模型中User模型中,关于密码加密"""

    def test_password_setter(self, password):
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self, password):
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        u1 = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u1.password_hash != u2.password_hash)

    def test_roles_and_permissions(self):
        """测试用户角色和权限问题"""
        Role.insert_roles()
        u = User(email='test@example.com', password='test')
        self.assertTrue(u.can(Permission.WRITE_ARTICLES))
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertTrue(u.can(Permission.FOLLOW))
        self.assertFalse(u.can(Permission.MODERATE_COMMENTS))
        self.assertFalse(u.can(Permission.ADMINISTER))

