from flask import Blueprint
from app import db

migration_bp = Blueprint('migration', __name__)

@migration_bp.route('/admin/migrate', methods=['POST'])
def run_migration():
    """Agregar columnas faltantes sin borrar datos"""
    try:
        # Agregar columna email a barberos si no existe
        db.engine.execute('''
            ALTER TABLE barberos 
            ADD COLUMN IF NOT EXISTS email VARCHAR(100);
        ''')
        
        # Agregar duracion_minutos a servicios
        db.engine.execute('''
            ALTER TABLE servicios 
            ADD COLUMN IF NOT EXISTS duracion_minutos INTEGER;
        ''')
        
        return {'status': 'success', 'message': 'Migration completed'}, 200
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500
