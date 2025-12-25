from flask import request, jsonify
from app import db
from app.models import Barbero

def get_barberos():
    barberos = Barbero.query.all()
    return jsonify([b.to_dict() for b in barberos]), 200

def get_barbero(id):
    barbero = Barbero.query.get(id)
    if not barbero:
        return jsonify({'error': 'Barbero no encontrado'}), 404
    return jsonify(barbero.to_dict()), 200

def create_barbero():
    data = request.get_json()
    barbero = Barbero(nombre=data.get('nombre'), telefono=data.get('telefono'))
    db.session.add(barbero)
    db.session.commit()
    return jsonify(barbero.to_dict()), 201

def update_barbero(id):
    barbero = Barbero.query.get(id)
    if not barbero:
        return jsonify({'error': 'Barbero no encontrado'}), 404
    data = request.get_json()
    barbero.nombre = data.get('nombre', barbero.nombre)
    barbero.telefono = data.get('telefono', barbero.telefono)
    db.session.commit()
    return jsonify(barbero.to_dict()), 200

def delete_barbero(id):
    barbero = Barbero.query.get(id)
    if not barbero:
        return jsonify({'error': 'Barbero no encontrado'}), 404
    db.session.delete(barbero)
    db.session.commit()
    return jsonify({'message': 'Barbero eliminado'}), 200