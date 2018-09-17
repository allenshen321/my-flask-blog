import unittest
from app import create_app, db
from flask import current_app


class BasicsTestCase(unittest.TestCase):
    """基础功能测试"""
    def setUp(self):
        self.app = create_app('test_config')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exist(self):
        self.assertFalse(current_app is None)

    def test_is_test(self):
        self.assertTrue(current_app.config['TESTING'])

