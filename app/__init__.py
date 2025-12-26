import os
from flask import Flask
from flask_cors import CORS
from .models import db


def create_app():
    app = Flask(__name__)
    
    # Config - Usar PostgreSQL en Render, SQLite en local
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        # PostgreSQL en Render
        if database_url.startswith('postgresql://'):
            database_url = database_url.replace('postgresql://', 'postgresql+psycopg2://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # SQLite local
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///barberia.db'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Init DB
    db.init_app(app)
    CORS(app)
    
    # Registrar rutas básicas
    from app.routes import register_routes
    register_routes(app)
    
    # Registrar Blueprint de reportes
    from app.reportes import reportes_bp
    app.register_blueprint(reportes_bp)
    
    # Health check
    @app.route('/api/health', methods=['GET'])
    def health():
        return {'status': 'ok'}, 200
    
    with app.app_context():
        db.create_all()
    
    return app
