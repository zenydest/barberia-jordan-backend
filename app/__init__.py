from flask import Flask
from flask_cors import CORS
from .models import db

def create_app():
    app = Flask(__name__)
    
    # Config
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
