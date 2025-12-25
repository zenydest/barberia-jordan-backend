from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Crear db aquí
db = SQLAlchemy()

class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'telefono': self.telefono,
            'email': self.email,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None
        }

class Barbero(db.Model):
    __tablename__ = 'barberos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'email': self.email,
            'telefono': self.telefono,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None
        }

class Servicio(db.Model):
    __tablename__ = 'servicios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    duracion_minutos = db.Column(db.Integer)

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'precio': self.precio,
            'duracion_minutos': self.duracion_minutos
        }

class Cobro(db.Model):
    __tablename__ = 'cobros'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    barbero_id = db.Column(db.Integer, db.ForeignKey('barberos.id'), nullable=False)
    servicio_id = db.Column(db.Integer, db.ForeignKey('servicios.id'), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    
    cliente = db.relationship('Cliente', backref='cobros')
    barbero = db.relationship('Barbero', backref='cobros')
    servicio = db.relationship('Servicio', backref='cobros')

    def to_dict(self):
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'barbero_id': self.barbero_id,
            'servicio_id': self.servicio_id,
            'monto': self.monto,
            'fecha': self.fecha.isoformat() if self.fecha else None
        }