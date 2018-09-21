import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    """定义基类配置文件"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TERMDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 电子邮件配置
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 465
    # MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')

    # 每页显示数量控制
    FLASK_POSTS_PER_PAGE_COUNT = 20
    FLASK_FOLLOW_PER_PAGE_COUNT = 20
    FLASK_COMMENT_PER_PAGE_COUNT = 5

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    """开发环境配置项"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_MYSQL_DEV_DATABASE_URL') or 'sqlite:////' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    """测试环境配置项"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_MYSQL_TEST_DATABASE_URL') or 'sqlite:////' + os.path.join(basedir, 'data-test.sqlite')


class ProductConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_MYSQL_PRODUCT_DATABASE_URL') or 'sqlite:////' + os.path.join(basedir, 'data-product.sqlite')


config = {
    'dev_config': DevelopmentConfig,
    'test_config': TestingConfig,
    'product_config': ProductConfig,

    'default': DevelopmentConfig
}


