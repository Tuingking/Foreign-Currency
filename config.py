import os
from dotenv import load_dotenv
from pathlib import Path  # python3 only
env_path = Path('.') / '.env'
load_dotenv(verbose=True, dotenv_path=env_path)

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'h4rDt0Gu3sSsTr1nGz'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:password@localhost/foreign_currency'


class TestingConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'dev.db')


class DockerConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:password@mysql/foreign_currency'


config = {
    'dev': DevelopmentConfig,
    'test': TestingConfig,
    'docker': DockerConfig,

    'default': DevelopmentConfig
}
