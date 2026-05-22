from app.extensions import ma
from app.models import Mechanics

class MechanicsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanics
        load_instance = False
        include_fk = True

mechanic_schema = MechanicsSchema(exclude=('password',))
# allow partial updates
mechanic_load_schema = MechanicsSchema(partial=True)
mechanic_login_schema = MechanicsSchema(only=('email', 'password'))
mechanics_schema = MechanicsSchema(many=True, exclude=('password',))
