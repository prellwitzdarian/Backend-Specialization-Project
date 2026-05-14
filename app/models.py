
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select
from sqlalchemy.orm import Mapped, mapped_column   

from marshmallow import ValidationError

from .extensions import db

#relationship table

mechanic_service = db.Table(
    'mechanic_service',
    db.Column('mechanic_id', db.Integer, db.ForeignKey('mechanics.id')),
    db.Column('service_ticket_id', db.Integer, db.ForeignKey('service_tickets.id'))
)



#tables

class Customers(db.Model):
    __tablename__ = 'customers'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(50), nullable=False)
    email: Mapped[str] = mapped_column(db.String(100), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(db.String(20), nullable=False)
    
    service_ticket: Mapped[list['Service_tickets']] = db.relationship('Service_tickets', back_populates='customer')

class Service_tickets(db.Model):
    __tablename__ = 'service_tickets'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    service_date: Mapped[str] = mapped_column(db.String(20), nullable=False)
    issue_description: Mapped[str] = mapped_column(db.Text, nullable=False)
    vin: Mapped[str] = mapped_column(db.String(20), nullable=False)
    
    customer: Mapped['Customers'] = db.relationship('Customers', back_populates='service_ticket')

    mechanics: Mapped[list['Mechanics']] = db.relationship('Mechanics', secondary=mechanic_service, backref='service_tickets')
    
    
class Mechanics(db.Model):
    __tablename__ = 'mechanics'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(50), nullable=False)
    email: Mapped[str] = mapped_column(db.String(100), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(db.String(20), nullable=False)
    salary: Mapped[float] = mapped_column(db.Float, nullable=False)
    