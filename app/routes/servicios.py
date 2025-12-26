from flask import Blueprint, request, jsonify
from ..models import db, Servicio


def get_servicios_bp():
    bp = Blueprint('servicios', __name__)
    
    @bp.route('', methods=['GET'])
    def get_servicios():
        servicios = Servicio.query.all()
        return jsonify([s.to_dict() for s in servicios]), 200

    @bp.route('/<int:id>', methods=['GET'])
    def get_servicio(id):
        servicio = Servicio.query.get(id)
        if not servicio:
            return jsonify({'error': 'Servicio no encontrado'}), 404
        return jsonify(servicio.to_dict()), 200

    @bp.route('', methods=['POST'])
    def create_servicio():
        data = request.get_json()
        servicio = Servicio(nombre=data.get('nombre'), precio=data.get('precio'), duracion_minutos=data.get('duracion_minutos'))
        db.session.add(servicio)
        db.session.commit()
        return jsonify(servicio.to_dict()), 201

    @bp.route('/<int:id>', methods=['PUT'])
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

    @bp.route('/<int:id>', methods=['DELETE'])
    def delete_servicio(id):
        servicio = Servicio.query.get(id)
        if not servicio:
            return jsonify({'error': 'Servicio no encontrado'}), 404
        db.session.delete(servicio)
        db.session.commit()
        return jsonify({'message': 'Servicio eliminado'}), 200

    return bp
