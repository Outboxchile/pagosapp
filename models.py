from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Persona(db.Model):
    __tablename__ = "personas"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String, unique=True, nullable=False)
    porcentaje = db.Column(db.Float, nullable=False)

class Pago(db.Model):
    __tablename__ = "pagos"
    id = db.Column(db.Integer, primary_key=True)
    cliente = db.Column(db.String, nullable=False)
    monto = db.Column(db.Float, nullable=False)
    fecha_programada = db.Column(db.Date, nullable=False)
    fecha_pagado = db.Column(db.Date, nullable=True)
    comisiones = db.relationship("Comision", back_populates="pago")

class Comision(db.Model):
    __tablename__ = "comisiones"
    id = db.Column(db.Integer, primary_key=True)
    pago_id = db.Column(db.Integer, db.ForeignKey("pagos.id"), nullable=False)
    persona_id = db.Column(db.Integer, db.ForeignKey("personas.id"), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    pago = db.relationship("Pago", back_populates="comisiones")
    persona = db.relationship("Persona")

