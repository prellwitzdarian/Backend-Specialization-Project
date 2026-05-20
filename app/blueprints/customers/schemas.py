from app.extensions import ma
from app.models import Customers

class CustomersSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customers
        load_instance = True
        include_fk = True

customer_schema = CustomersSchema(exclude=('password',))
customers_schema = CustomersSchema(many=True, exclude=('password',))
customer_load_schema = CustomersSchema()
login_schema = CustomersSchema(only=('email', 'password'))