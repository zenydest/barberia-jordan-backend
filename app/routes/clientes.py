from flask import request, jsonify
from app import db
from app.models import Cliente

def get_clientes():
    clientes = Cliente.query.all()
    return jsonify([c.to_dict() for c in clientes]), 200

def get_cliente(id):
    cliente = Cliente.query.get(id)
    if not cliente:
        return jsonify({'error': 'Cliente no encontrado'}), 404
    return jsonify(cliente.to_dict()), 200

def create_cliente():
    data = request.get_json()
    cliente = Cliente(nombre=data.get('nombre'), telefono=data.get('telefono'))
    db.session.add(cliente)
    db.session.commit()
    return jsonify(cliente.to_dict()), 201

def update_cliente(id):
    cliente = Cliente.query.get(id)
    if not cliente:
        return jsonify({'error': 'Cliente no encontrado'}), 404
    data = request.get_json()
    cliente.nombre = data.get('nombre', cliente.nombre)
    cliente.telefono = data.get('telefono', cliente.telefono)
    db.session.commit()
    return jsonify(cliente.to_dict()), 200

def delete_cliente(id):
    cliente = Cliente.query.get(id)
    if not cliente:
        return jsonify({'error': 'Cliente no encontrado'}), 404
    db.session.delete(cliente)
    db.session.commit()
    return jsonify({'message': 'Cliente eliminado'}), 200