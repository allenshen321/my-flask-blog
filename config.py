import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    """定义基类配置文件"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TERMDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    """开发环境配置项"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_MYSQL_DATABASE_URL') + 'flask_dev_data' or 'sqlite:////' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    """测试环境配置项"""
    SQLALCHEMY_DATABASW_URI = os.environ.get('SQLALCHEMY_MYSQL_DATABASE_URL') + 'flask_test_data' or 'sqlite:////' + os.path.join(basedir, 'data-test.sqlite')


class ProductConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_MYSQL_DATABASE_URL') + 'flask_product_data' or 'sqlite:////' + os.path.join(basedir, 'data-product.sqlite')


config = {
    'dev_config': DevelopmentConfig,
    'test_config': TestingConfig,
    'product_config': ProductConfig,

    'default': DevelopmentConfig
}


