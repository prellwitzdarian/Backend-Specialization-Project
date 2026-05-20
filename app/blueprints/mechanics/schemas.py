from app.extensions import ma
from app.models import Mechanics

class MechanicsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanics
        load_instance = True
        include_fk = True

mechanic_schema = MechanicsSchema(exclude=('password',))
mechanic_load_schema = MechanicsSchema()
mechanic_login_schema = MechanicsSchema(only=('email', 'password'))
mechanics_schema = MechanicsSchema(many=True, exclude=('password',))
