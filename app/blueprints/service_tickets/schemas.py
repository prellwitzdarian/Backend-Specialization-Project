from marshmallow import Schema, fields
from app.extensions import ma
from app.models import Service_tickets

class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Service_tickets
        load_instance = True
        include_fk = True

service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)


class EditServiceTicketSchema(Schema):
    add_mechanic_ids = fields.List(fields.Int(), load_default=[])
    remove_mechanic_ids = fields.List(fields.Int(), load_default=[])

edit_service_ticket_schema = EditServiceTicketSchema()
