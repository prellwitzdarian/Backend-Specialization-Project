import os

class ProductionConfig:
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    CACHE_TYPE = "SimpleCache"


class DevelopmentConfig:
    SECRET_KEY = 'super-secret-secrets'
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:hello@localhost/specialization_api'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300
    RATELIMIT_DEFAULT = '200 per day;50 per hour'

class TestingConfig:
    SECRET_KEY = 'test-secret'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = True
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300
    RATELIMIT_DEFAULT = '1000 per day'

class ProductionConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'production-secret'
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300
    RATELIMIT_DEFAULT = '200 per day;50 per hour'
    
