from app.extensions import ma
from app.models import Inventory

class InventorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory
        load_instance = False
        include_fk = True
        exclude = ('service_tickets',)

inventory_schema = InventorySchema()
inventories_schema = InventorySchema(many=True)
