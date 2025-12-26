from flask import Blueprint, request, jsonify
from ..models import db, Cobro


def get_cobros_bp():
    bp = Blueprint('cobros', __name__)
    
    @bp.route('', methods=['GET'])
    def get_cobros():
        cobros = Cobro.query.all()
        return jsonify([c.to_dict() for c in cobros]), 200

    @bp.route('/<int:id>', methods=['GET'])
    def get_cobro(id):
        cobro = Cobro.query.get(id)
        if not cobro:
            return jsonify({'error': 'Cobro no encontrado'}), 404
        return jsonify(cobro.to_dict()), 200

    @bp.route('', methods=['POST'])
    def create_cobro():
        data = request.get_json()
        cobro = Cobro(cliente_id=data.get('cliente_id'), barbero_id=data.get('barbero_id'), servicio_id=data.get('servicio_id'), monto=data.get('monto'))
        db.session.add(cobro)
        db.session.commit()
        return jsonify(cobro.to_dict()), 201

    @bp.route('/<int:id>', methods=['PUT'])
    def update_cobro(id):
        cobro = Cobro.query.get(id)
        if not cobro:
            return jsonify({'error': 'Cobro no encontrado'}), 404
        data = request.get_json()
        cobro.monto = data.get('monto', cobro.monto)
        db.session.commit()
        return jsonify(cobro.to_dict()), 200

    @bp.route('/<int:id>', methods=['DELETE'])
    def delete_cobro(id):
        cobro = Cobro.query.get(id)
        if not cobro:
            return jsonify({'error': 'Cobro no encontrado'}), 404
        db.session.delete(cobro)
        db.session.commit()
        return jsonify({'message': 'Cobro eliminado'}), 200

    return bp
