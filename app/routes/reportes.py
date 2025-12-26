from flask import Blueprint, jsonify, request
from ..models import db, Cobro, Servicio, Cliente, Barbero
from datetime import datetime, timedelta
from sqlalchemy import func


def get_reportes_bp():
    bp = Blueprint('reportes', __name__)
    
    @bp.route('/diario', methods=['GET'])
    def reporte_diario():
        hoy = datetime.utcnow().date()
        cobros = Cobro.query.filter(db.func.date(Cobro.fecha) == hoy).all()
        total = sum(c.monto for c in cobros)
        cantidad = len(cobros)
        promedio = (total / cantidad) if cantidad > 0 else 0
        return jsonify({
            'fecha': str(hoy),
            'total': float(total),
            'cantidad': cantidad,
            'promedio': float(promedio),
            'cobros': [c.to_dict() for c in cobros]
        }), 200

    @bp.route('/servicios-vendidos', methods=['GET'])
    def servicios_mas_vendidos():
        resultados = db.session.query(
            Cobro.servicio_id,
            Servicio.nombre.label('servicio_nombre'),
            func.count(Cobro.id).label('cantidad'),
            func.sum(Cobro.monto).label('ingresos')
        ).join(Servicio, Cobro.servicio_id == Servicio.id).group_by(
            Cobro.servicio_id, Servicio.nombre
        ).order_by(func.count(Cobro.id).desc()).limit(10).all()
        
        data = [{
            'servicio_id': r[0],
            'servicio_nombre': r[1],
            'cantidad': r[2],
            'ingresos': float(r[3] or 0)
        } for r in resultados]
        return jsonify(data), 200

    return bp
