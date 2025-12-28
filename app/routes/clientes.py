from flask import Blueprint, request, jsonify
from ..models import db, Cliente

def get_clientes_bp():
    bp = Blueprint('clientes', __name__)

    @bp.route('', methods=['GET'])
    def get_clientes():
        clientes = Cliente.query.all()
        return jsonify([c.to_dict() for c in clientes]), 200

    @bp.route('/<int:id>', methods=['GET'])
    def get_cliente(id):
        cliente = Cliente.query.get(id)
        if not cliente:
            return jsonify({'error': 'Cliente no encontrado'}), 404
        return jsonify(cliente.to_dict()), 200

    @bp.route('', methods=['POST'])
    def create_cliente():
        data = request.get_json()
        cliente = Cliente(
            nombre=data.get('nombre'),
            telefono=data.get('telefono'),
            email=data.get('email')
        )
        db.session.add(cliente)
        db.session.commit()
        return jsonify(cliente.to_dict()), 201

    @bp.route('/<int:id>', methods=['PUT'])
    def update_cliente(id):
        cliente = Cliente.query.get(id)
        if not cliente:
            return jsonify({'error': 'Cliente no encontrado'}), 404

        data = request.get_json()
        cliente.nombre = data.get('nombre', cliente.nombre)
        cliente.telefono = data.get('telefono', cliente.telefono)
        cliente.email = data.get('email', cliente.email)

        db.session.commit()
        return jsonify(cliente.to_dict()), 200

    @bp.route('/<int:id>', methods=['DELETE'])
    def delete_cliente(id):
        cliente = Cliente.query.get(id)
        if not cliente:
            return jsonify({'error': 'Cliente no encontrado'}), 404

        db.session.delete(cliente)
        db.session.commit()
        return jsonify({'message': 'Cliente eliminado'}), 200

    return bp
