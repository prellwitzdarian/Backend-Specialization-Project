from app.extensions import ma
from app.models import Customers

class CustomersSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customers

customer_schema = CustomersSchema()
customers_schema = CustomersSchema(many=True)
