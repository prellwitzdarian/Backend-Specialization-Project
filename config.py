class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:hello@localhost/specialization_api'
    DEBUG = True
    
class TestingConfig:
    pass

class ProductionConfig:
    pass 
    
