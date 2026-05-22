from app.extensions import ma
from app.models import Customers

class CustomersSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customers
        load_instance = False
        include_fk = True

customer_schema = CustomersSchema(exclude=('password',))
customers_schema = CustomersSchema(many=True, exclude=('password',))
# Full load schema for creation
customer_load_schema = CustomersSchema()
# Partial schema for updates
customer_update_schema = CustomersSchema(partial=True)
login_schema = CustomersSchema(only=('email', 'password'))