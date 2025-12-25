from flask import request, jsonify
from app import db
from app.models import Cobro

def get_cobros():
    cobros = Cobro.query.all()
    return jsonify([c.to_dict() for c in cobros]), 200

def get_cobro(id):
    cobro = Cobro.query.get(id)
    if not cobro:
        return jsonify({'error': 'Cobro no encontrado'}), 404
    return jsonify(cobro.to_dict()), 200

def create_cobro():
    data = request.get_json()
    cobro = Cobro(cliente_id=data.get('cliente_id'), barbero_id=data.get('barbero_id'), servicio_id=data.get('servicio_id'), monto=data.get('monto'))
    db.session.add(cobro)
    db.session.commit()
    return jsonify(cobro.to_dict()), 201

def update_cobro(id):
    cobro = Cobro.query.get(id)
    if not cobro:
        return jsonify({'error': 'Cobro no encontrado'}), 404
    data = request.get_json()
    cobro.monto = data.get('monto', cobro.monto)
    db.session.commit()
    return jsonify(cobro.to_dict()), 200

def delete_cobro(id):
    cobro = Cobro.query.get(id)
    if not cobro:
        return jsonify({'error': 'Cobro no encontrado'}), 404
    db.session.delete(cobro)
    db.session.commit()
    return jsonify({'message': 'Cobro eliminado'}), 200