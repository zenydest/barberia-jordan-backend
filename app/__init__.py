import os
from flask import Flask
from flask_cors import CORS
from .models import db


def create_app():
    app = Flask(__name__)
    
    # Config
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        if database_url.startswith('postgresql://'):
            database_url = database_url.replace('postgresql://', 'postgresql+psycopg2://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///barberia.db'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    CORS(app)
    
    # ✅ Registrar blueprints
    from .routes import barberos_bp, servicios_bp, cobros_bp, clientes_bp, reportes_bp, exportar_bp
    
    app.register_blueprint(barberos_bp, url_prefix='/barberos')
    app.register_blueprint(servicios_bp, url_prefix='/servicios')
    app.register_blueprint(cobros_bp, url_prefix='/cobros')
    app.register_blueprint(clientes_bp, url_prefix='/clientes')
    app.register_blueprint(reportes_bp, url_prefix='/reportes')
    app.register_blueprint(exportar_bp, url_prefix='/exportar')
    
    @app.route('/api/health', methods=['GET'])
    def health():
        return {'status': 'ok'}, 200
    
    with app.app_context():
        db.create_all()
    
    return app
