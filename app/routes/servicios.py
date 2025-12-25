from flask import request, jsonify
from app import db
from app.models import Servicio

def get_servicios():
    servicios = Servicio.query.all()
    return jsonify([s.to_dict() for s in servicios]), 200

def get_servicio(id):
    servicio = Servicio.query.get(id)
    if not servicio:
        return jsonify({'error': 'Servicio no encontrado'}), 404
    return jsonify(servicio.to_dict()), 200

def create_servicio():
    data = request.get_json()
    servicio = Servicio(nombre=data.get('nombre'), precio=data.get('precio'), duracion_minutos=data.get('duracion_minutos'))
    db.session.add(servicio)
    db.session.commit()
    return jsonify(servicio.to_dict()), 201

def update_servicio(id):
    servicio = Servicio.query.get(id)
    if not servicio:
        return jsonify({'error': 'Servicio no encontrado'}), 404
    data = request.get_json()
    servicio.nombre = data.get('nombre', servicio.nombre)
    servicio.precio = data.get('precio', servicio.precio)
    servicio.duracion_minutos = data.get('duracion_minutos', servicio.duracion_minutos)
    db.session.commit()
    return jsonify(servicio.to_dict()), 200

def delete_servicio(id):
    servicio = Servicio.query.get(id)
    if not servicio:
        return jsonify({'error': 'Servicio no encontrado'}), 404
    db.session.delete(servicio)
    db.session.commit()
    return jsonify({'message': 'Servicio eliminado'}), 200