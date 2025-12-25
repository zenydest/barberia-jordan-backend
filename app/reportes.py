from flask import jsonify, request, Blueprint
from app import db
from app.models import Cobro, Servicio
from datetime import datetime, timedelta
from sqlalchemy import func

reportes_bp = Blueprint('reportes', __name__, url_prefix='/api/reportes')

@reportes_bp.route('/diario', methods=['GET'])
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

@reportes_bp.route('/semanal', methods=['GET'])
def reporte_semanal():
    hoy = datetime.utcnow().date()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    cobros = Cobro.query.filter(
        db.func.date(Cobro.fecha) >= inicio_semana,
        db.func.date(Cobro.fecha) <= hoy
    ).all()
    total = sum(c.monto for c in cobros)
    cantidad = len(cobros)
    promedio = (total / cantidad) if cantidad > 0 else 0
    return jsonify({
        'periodo': f'{inicio_semana} a {hoy}',
        'total': float(total),
        'cantidad': cantidad,
        'promedio': float(promedio),
        'cobros': [c.to_dict() for c in cobros]
    }), 200

@reportes_bp.route('/mensual', methods=['GET'])
def reporte_mensual():
    hoy = datetime.utcnow().date()
    inicio_mes = hoy.replace(day=1)
    cobros = Cobro.query.filter(
        db.func.date(Cobro.fecha) >= inicio_mes,
        db.func.date(Cobro.fecha) <= hoy
    ).all()
    total = sum(c.monto for c in cobros)
    cantidad = len(cobros)
    promedio = (total / cantidad) if cantidad > 0 else 0
    return jsonify({
        'mes': str(hoy),
        'total': float(total),
        'cantidad': cantidad,
        'promedio': float(promedio),
        'cobros': [c.to_dict() for c in cobros]
    }), 200

@reportes_bp.route('/anual', methods=['GET'])
def reporte_anual():
    hoy = datetime.utcnow().date()
    inicio_año = hoy.replace(month=1, day=1)
    cobros = Cobro.query.filter(
        db.func.date(Cobro.fecha) >= inicio_año,
        db.func.date(Cobro.fecha) <= hoy
    ).all()
    total = sum(c.monto for c in cobros)
    cantidad = len(cobros)
    promedio = (total / cantidad) if cantidad > 0 else 0
    return jsonify({
        'año': str(hoy.year),
        'total': float(total),
        'cantidad': cantidad,
        'promedio': float(promedio),
        'cobros': [c.to_dict() for c in cobros]
    }), 200

@reportes_bp.route('/servicios-vendidos', methods=['GET'])
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

@reportes_bp.route('/rango', methods=['GET'])
def reporte_rango_fechas():
    fecha_inicio = request.args.get('inicio')
    fecha_fin = request.args.get('fin')
    cobros = Cobro.query.filter(
        db.func.date(Cobro.fecha) >= fecha_inicio,
        db.func.date(Cobro.fecha) <= fecha_fin
    ).all()
    total = sum(c.monto for c in cobros)
    cantidad = len(cobros)
    promedio = (total / cantidad) if cantidad > 0 else 0
    return jsonify({
        'periodo': f'{fecha_inicio} a {fecha_fin}',
        'total': float(total),
        'cantidad': cantidad,
        'promedio': float(promedio),
        'cobros': [c.to_dict() for c in cobros]
    }), 200
