from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.pool import NullPool
from datetime import datetime, timedelta
import jwt
import os
from pathlib import Path
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash


load_dotenv()


app = Flask(__name__)


# ==================== CONFIGURACIÓN CORS - CRÍTICO ====================
CORS(app, 
     origins=["https://barberia-jordan-frontend.vercel.app", "http://localhost:3000", "http://localhost:5173"],
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])


# ==================== CONFIGURACIÓN DE BD ====================

app.config['ENV'] = 'production' if os.getenv('DATABASE_URL') else 'development'

DATABASE_URL = os.getenv('DATABASE_URL')


if DATABASE_URL:
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL.replace('postgresql://', 'postgresql+psycopg://', 1)
else:
    BASEDIR = Path(__file__).resolve().parent
    DATABASE_PATH = BASEDIR / 'instance' / 'barberia.db'
    DATABASE_PATH.parent.mkdir(exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'tu-clave-secreta-cambiar-en-produccion')
app.config['JWT_EXPIRATION_HOURS'] = 24
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'poolclass': NullPool,
}


db = SQLAlchemy(app)


@app.errorhandler(Exception)
def handle_db_error(error):
    """Maneja errores de conexión elegantemente"""
    if 'EOF detected' in str(error) or 'connection' in str(error).lower():
        db.session.remove()
        return jsonify({'error': 'Conexión temporal a BD - reintentar'}), 503
    print(f"❌ Error: {error}")
    return jsonify({'error': 'Error interno'}), 500


# ==================== MODELOS ====================


class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    rol = db.Column(db.String(20), default='barbero')
    estado = db.Column(db.String(20), default='activo')
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)


    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'nombre': self.nombre,
            'rol': self.rol,
            'estado': self.estado,
            'fecha_registro': self.fecha_registro.strftime('%Y-%m-%d')
        }


class Barbero(db.Model):
    __tablename__ = 'barberos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=True)
    telefono = db.Column(db.String(20), nullable=True)
    comision = db.Column(db.Float, default=20.0)
    estado = db.Column(db.String(20), default='activo')
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)


    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'email': self.email,
            'telefono': self.telefono,
            'comision': self.comision,
            'estado': self.estado,
            'fecha_registro': self.fecha_registro.strftime('%Y-%m-%d')
        }


class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=True)
    telefono = db.Column(db.String(20), nullable=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)


    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'email': self.email,
            'telefono': self.telefono,
            'fecha_registro': self.fecha_registro.strftime('%Y-%m-%d')
        }


class Servicio(db.Model):
    __tablename__ = 'servicios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    descripcion = db.Column(db.String(255))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)


    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'precio': self.precio,
            'descripcion': self.descripcion,
            'fecha_registro': self.fecha_registro.strftime('%Y-%m-%d')
        }


class Cita(db.Model):
    __tablename__ = 'citas'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=True)
    barbero_id = db.Column(db.Integer, db.ForeignKey('barberos.id'), nullable=False)
    servicio_id = db.Column(db.Integer, db.ForeignKey('servicios.id'), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    notas = db.Column(db.String(255))
    
    cliente = db.relationship('Cliente', backref='citas')
    barbero = db.relationship('Barbero', backref='citas')
    servicio = db.relationship('Servicio', backref='citas')


    def to_dict(self):
        return {
            'id': self.id,
            'cliente': self.cliente.nombre if self.cliente else 'Cliente no registrado',
            'cliente_id': self.cliente_id,
            'barbero': self.barbero.nombre,
            'barbero_id': self.barbero_id,
            'servicio': self.servicio.nombre,
            'servicio_id': self.servicio_id,
            'precio': self.precio,
            'fecha': self.fecha.strftime('%Y-%m-%d %H:%M:%S'),
            'notas': self.notas
        }


# ==================== FUNCIONES DE AUTENTICACIÓN ====================


def generar_token(usuario_id):
    payload = {
        'usuario_id': usuario_id,
        'exp': datetime.utcnow() + timedelta(hours=app.config['JWT_EXPIRATION_HOURS'])
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')


def verificar_token(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['usuario_id']
    except:
        return None


def get_token_from_request():
    """Extrae el token del header Authorization"""
    if 'Authorization' not in request.headers:
        return None
    
    try:
        auth_header = request.headers['Authorization']
        token = auth_header.split(" ")[1]
        return token
    except IndexError:
        return None


def verify_token_and_get_user():
    """Verifica el token y retorna el usuario o None"""
    token = get_token_from_request()
    
    if not token:
        return None
    
    usuario_id = verificar_token(token)
    if not usuario_id:
        return None
    
    usuario = Usuario.query.get(usuario_id)
    return usuario


# ==================== RUTAS DE AUTENTICACIÓN ====================


@app.route('/api/auth/registro', methods=['POST', 'OPTIONS'])
def registro():
    if request.method == 'OPTIONS':
        return '', 200
    
    data = request.get_json()
    
    if not data or not all(k in data for k in ['email', 'password', 'nombre']):
        return jsonify({'error': 'Email, password y nombre son requeridos'}), 400
    
    if Usuario.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'El email ya está registrado'}), 409
    
    nuevo_usuario = Usuario(
        email=data['email'],
        nombre=data['nombre'],
        rol=data.get('rol', 'barbero')
    )
    nuevo_usuario.set_password(data['password'])
    db.session.add(nuevo_usuario)
    db.session.commit()
    
    token = generar_token(nuevo_usuario.id)
    return jsonify({
        'mensaje': 'Usuario registrado exitosamente',
        'token': token,
        'usuario': nuevo_usuario.to_dict()
    }), 201


@app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200
    
    data = request.get_json()
    
    if not data or not all(k in data for k in ['email', 'password']):
        return jsonify({'error': 'Email y password son requeridos'}), 400
    
    usuario = Usuario.query.filter_by(email=data['email']).first()
    
    if not usuario or not usuario.check_password(data['password']):
        return jsonify({'error': 'Email o contraseña incorrectos'}), 401
    
    token = generar_token(usuario.id)
    return jsonify({
        'mensaje': 'Login exitoso',
        'token': token,
        'usuario': usuario.to_dict()
    }), 200


@app.route('/api/auth/me', methods=['GET', 'OPTIONS'])
def get_current_usuario():
    if request.method == 'OPTIONS':
        return '', 200
    
    usuario = verify_token_and_get_user()
    
    if not usuario:
        return jsonify({'error': 'Token inválido o no encontrado'}), 401
    
    return jsonify(usuario.to_dict()), 200


@app.route('/api/auth/logout', methods=['POST', 'OPTIONS'])
def logout():
    if request.method == 'OPTIONS':
        return '', 200
    
    usuario = verify_token_and_get_user()
    
    if not usuario:
        return jsonify({'error': 'Token inválido o no encontrado'}), 401
    
    return jsonify({'mensaje': 'Logout exitoso'}), 200


# ==================== RUTAS BARBEROS ====================


@app.route('/api/barberos', methods=['GET', 'OPTIONS'])
def get_barberos():
    if request.method == 'OPTIONS':
        return '', 200
    
    usuario = verify_token_and_get_user()
    
    if not usuario:
        return jsonify({'error': 'Token inválido o no encontrado'}), 401
    
    if usuario.rol != 'admin':
        return jsonify({'error': 'Acceso denegado. Se requiere rol de administrador'}), 403
    
    try:
        barberos = Barbero.query.all()
        return jsonify([barbero.to_dict() for barbero in barberos]), 200
    except Exception as e:
        print(f"❌ Error en get_barberos: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/barberos', methods=['POST', 'OPTIONS'])
def crear_barbero():
    if request.method == 'OPTIONS':
        return '', 200
    
    usuario = verify_token_and_get_user()
    
    if not usuario:
        return jsonify({'error': 'Token inválido o no encontrado'}), 401
    
    if usuario.rol != 'admin':
        return jsonify({'error': 'Acceso denegado. Se requiere rol de administrador'}), 403
    
    data = request.get_json()
    
    if not data or not data.get('nombre', '').strip():
        return jsonify({'error': 'El nombre es requerido'}), 400
    
    nuevo_barbero = Barbero(
        nombre=data['nombre'].strip(),
        email=data.get('email', '').strip() if data.get('email') else None,
        telefono=data.get('telefono', '').strip() if data.get('telefono') else None,
        comision=float(data.get('comision', 20.0))
    )
    
    db.session.add(nuevo_barbero)
    db.session.commit()
    
    return jsonify(nuevo_barbero.to_dict()), 201


@app.route('/api/barberos/<int:id>', methods=['PUT', 'OPTIONS'])
def actualizar_barbero(id):
    if request.method == 'OPTIONS':
        return '', 200
    
    usuario = verify_token_and_get_user()
    
    if not usuario:
        return jsonify({'error': 'Token inválido o no encontrado'}), 401
    
    if usuario.rol != 'admin':
        return jsonify({'error': 'Acceso denegado. Se requiere rol de administrador'}), 403
    
    barbero = Barbero.query.get(id)
    
    if not barbero:
        return jsonify({'error': 'Barbero no encontrado'}), 404
    
    data = request.get_json()
    
    if 'nombre' in data:
        barbero.nombre = data['nombre']
    if 'email' in data:
        barbero.email = data['email']
    if 'telefono' in data:
        barbero.telefono = data['telefono']
    if 'comision' in data:
        barbero.comision = float(data['comision'])
    if 'estado' in data:
        barbero.estado = data['estado']
    
    db.session.commit()
    
    return jsonify(barbero.to_dict()), 200


@app.route('/api/barberos/<int:id>', methods=['DELETE', 'OPTIONS'])
def eliminar_barbero(id):
    if request.method == 'OPTIONS':
        return '', 200
    
    usuario = verify_token_and_get_user()
    
    if not usuario:
        return jsonify({'error': 'Token inválido o no encontrado'}), 401
    
    if usuario.rol != 'admin':
        return jsonify({'error': 'Acceso denegado. Se requiere rol de administrador'}), 403
    
    barbero = Barbero.query.get(id)
    
    if not barbero:
        return jsonify({'error': 'Barbero no encontrado'}), 404
    
    db.session.delete(barbero)
    db.session.commit()
    
    return jsonify({'mensaje': 'Barbero eliminado correctamente'}), 200


# ==================== RUTAS CLIENTES ====================


@app.route('/api/clientes', methods=['GET', 'OPTIONS'])
def get_clientes():
    if request.method == 'OPTIONS':
        return '', 200
    
    usuario = verify_token_and_get_user()
    
    if not usuario:
        return jsonify({'error': 'Token inválido o no encontrado'}), 401
    
    try:
        clientes = Cliente.query.all()
        return jsonify([cliente.to_dict() for cliente in clientes]), 200
    except Exception as e:
        print(f"❌ Error en get_clientes: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/clientes', methods=['POST', 'OPTIONS'])
def crear_cliente():
    if request.method == 'OPTIONS':
        return '', 200
    
    usuario = verify_token_and_get_user()
    
    if not usuario:
        return jsonify({'error': 'Token inválido o no encontrado'}), 401
    
    data = request.get_json()
    
    if not data or not data.get('nombre', '').strip():
        return jsonify({'error': 'El nombre es requerido'}), 400
    
    nuevo_cliente = Cliente(
        nombre=data['nombre'].strip(),
        email=data.get('email', '').strip() if data.get('email') else None,
        telefono=data.get('telefono', '').strip() if data.get('telefono') else None
    )
    
    db.session.add(nuevo_cliente)
    db.session.commit()
    
    return jsonify(nuevo_cliente.to_dict()), 201


@app.route('/api/clientes/<int:id>', methods=['PUT', 'OPTIONS'])
def actualizar_cliente(id):
    if request.method == 'OPTIONS':
        return '', 200
    
    usuario = verify_token_and_get_user()
    
    if not usuario:
        return jsonify({'error': 'Token inválido o no encontrado'}), 401
    
    cliente = Cliente.query.get(id)
    
    if not cliente:
        return jsonify({'error': 'Cliente no encontrado'}), 404
    
    data = request.get_json()
    
    if 'nombre' in data:
        cliente.nombre = data['nombre']
    if 'email' in data:
        cliente.email = data['email']
    if 'telefono' in data:
        cliente.telefono = data['telefono']
    
    db.session.commit()
    
    return jsonify(cliente.to_dict()), 200


@app.route('/api/clientes/<int:id>', methods=['DELETE', 'OPTIONS'])
def eliminar_cliente(id):
    if request.method == 'OPTIONS':
        return '', 200
    
    usuario = verify_token_and_get_user()
    
    if not usuario:
        return jsonify({'error': 'Token inválido o no encontrado'}), 401
    
    cliente = Cliente.query.get(id)
    
    if not cliente:
        return jsonify({'error': 'Cliente no encontrado'}), 404
    
    db.session.delete(cliente)
    db.session.commit()
    
    return jsonify({'mensaje': 'Cliente eliminado correctamente'}), 200


# ==================== RUTAS SERVICIOS ====================


@app.route('/api/servicios', methods=['GET', 'OPTIONS'])
def get_servicios():
    if request.method == 'OPTIONS':
        return '', 200
    
    usuario = verify_token_and_get_user()
    
    if not usuario:
        return jsonify({'error': 'Token inválido o no encontrado'}), 401
    
    if usuario.rol != 'admin':
        return jsonify({'error': 'Acceso denegado. Se requiere rol de administrador'}), 403
    
    try:
        servicios = Servicio.query.all()
        return jsonify([servicio.to_dict() for servicio in servicios]), 200
    except Exception as e:
        print(f"❌ Error en get_servicios: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/servicios', methods=['POST', 'OPTIONS'])
def crear_servicio():
    if request.method == 'OPTIONS':
        return '', 200
    
    usuario = verify_token_and_get_user()
    
    if not usuario:
        return jsonify({'error': 'Token inválido o no encontrado'}), 401
    
    if usuario.rol != 'admin':
        return jsonify({'error': 'Acceso denegado. Se requiere rol de administrador'}), 403
    
    data = request.get_json()
    
    if not data or not data.get('nombre') or not data.get('precio'):
        return jsonify({'error': 'Nombre y precio son requeridos'}), 400
    
    nuevo_servicio = Servicio(
        nombre=data['nombre'],
        precio=data['precio'],
        descripcion=data.get('descripcion', '')
    )
    
    db.session.add(nuevo_servicio)
    db.session.commit()
    
    return jsonify(nuevo_servicio.to_dict()), 201


@app.route('/api/servicios/<int:id>', methods=['PUT', 'OPTIONS'])
def actualizar_servicio(id):
    if request.method == 'OPTIONS':
        return '', 200
    
    usuario = verify_token_and_get_user()
    
    if not usuario:
        return jsonify({'error': 'Token inválido o no encontrado'}), 401
    
    if usuario.rol != 'admin':
        return jsonify({'error': 'Acceso denegado. Se requiere rol de administrador'}), 403
    
    servicio = Servicio.query.get(id)
    
    if not servicio:
        return jsonify({'error': 'Servicio no encontrado'}), 404
    
    data = request.get_json()
    
    if 'nombre' in data:
        servicio.nombre = data['nombre']
    if 'precio' in data:
        servicio.precio = data['precio']
    if 'descripcion' in data:
        servicio.descripcion = data['descripcion']
    
    db.session.commit()
    
    return jsonify(servicio.to_dict()), 200


@app.route('/api/servicios/<int:id>', methods=['DELETE', 'OPTIONS'])
def eliminar_servicio(id):
    if request.method == 'OPTIONS':
        return '', 200
    
    usuario = verify_token_and_get_user()
    
    if not usuario:
        return jsonify({'error': 'Token inválido o no encontrado'}), 401
    
    if usuario.rol != 'admin':
        return jsonify({'error': 'Acceso denegado. Se requiere rol de administrador'}), 403
    
    servicio = Servicio.query.get(id)
    
    if not servicio:
        return jsonify({'error': 'Servicio no encontrado'}), 404
    
    db.session.delete(servicio)
    db.session.commit()
    
    return jsonify({'mensaje': 'Servicio eliminado correctamente'}), 200


# ==================== RUTAS CITAS ====================


@app.route('/api/citas', methods=['GET', 'OPTIONS'])
def get_citas():
    if request.method == 'OPTIONS':
        return '', 200
    
    usuario = verify_token_and_get_user()
    
    if not usuario:
        return jsonify({'error': 'Token inválido o no encontrado'}), 401
    
    try:
        citas = Cita.query.order_by(Cita.fecha.desc()).all()
        return jsonify([cita.to_dict() for cita in citas]), 200
    except Exception as e:
        print(f"❌ Error en get_citas: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/citas', methods=['POST', 'OPTIONS'])
def crear_cita():
    if request.method == 'OPTIONS':
        return '', 200
    
    usuario = verify_token_and_get_user()
    
    if not usuario:
        return jsonify({'error': 'Token inválido o no encontrado'}), 401
    
    data = request.get_json()
    
    if not all(k in data for k in ['barbero_id', 'servicio_id', 'precio']):
        return jsonify({'error': 'Datos incompletos. Barbero, Servicio y Precio son requeridos'}), 400
    
    barbero = Barbero.query.get(data['barbero_id'])
    if not barbero:
        return jsonify({'error': 'Barbero no encontrado'}), 404
    
    servicio = Servicio.query.get(data['servicio_id'])
    if not servicio:
        return jsonify({'error': 'Servicio no encontrado'}), 404
    
    cliente_id = None
    if data.get('cliente_id'):
        cliente = Cliente.query.get(data['cliente_id'])
        if not cliente:
            return jsonify({'error': 'Cliente no encontrado'}), 404
        cliente_id = data['cliente_id']
    
    nueva_cita = Cita(
        cliente_id=cliente_id,
        barbero_id=data['barbero_id'],
        servicio_id=data['servicio_id'],
        precio=data['precio'],
        notas=data.get('notas', '')
    )
    
    db.session.add(nueva_cita)
    db.session.commit()
    
    return jsonify(nueva_cita.to_dict()), 201


@app.route('/api/citas/<int:id>', methods=['PUT', 'OPTIONS'])
def actualizar_cita(id):
    if request.method == 'OPTIONS':
        return '', 200
    
    usuario = verify_token_and_get_user()
    
    if not usuario:
        return jsonify({'error': 'Token inválido o no encontrado'}), 401
    
    cita = Cita.query.get(id)
    
    if not cita:
        return jsonify({'error': 'Cita no encontrada'}), 404
    
    data = request.get_json()
    
    if 'cliente_id' in data:
        if data['cliente_id']:
            cliente = Cliente.query.get(data['cliente_id'])
            if not cliente:
                return jsonify({'error': 'Cliente no encontrado'}), 404
        cita.cliente_id = data['cliente_id'] if data['cliente_id'] else None
    
    if 'barbero_id' in data:
        barbero = Barbero.query.get(data['barbero_id'])
        if not barbero:
            return jsonify({'error': 'Barbero no encontrado'}), 404
        cita.barbero_id = data['barbero_id']
    
    if 'servicio_id' in data:
        servicio = Servicio.query.get(data['servicio_id'])
        if not servicio:
            return jsonify({'error': 'Servicio no encontrado'}), 404
        cita.servicio_id = data['servicio_id']
    
    if 'precio' in data:
        cita.precio = data['precio']
    
    if 'notas' in data:
        cita.notas = data['notas']
    
    if 'fecha' in data:
        try:
            cita.fecha = datetime.fromisoformat(data['fecha'])
        except:
            return jsonify({'error': 'Formato de fecha inválido'}), 400
    
    db.session.commit()
    
    return jsonify(cita.to_dict()), 200


@app.route('/api/citas/<int:id>', methods=['DELETE', 'OPTIONS'])
def eliminar_cita(id):
    if request.method == 'OPTIONS':
        return '', 200
    
    usuario = verify_token_and_get_user()
    
    if not usuario:
        return jsonify({'error': 'Token inválido o no encontrado'}), 401
    
    cita = Cita.query.get(id)
    
    if not cita:
        return jsonify({'error': 'Cita no encontrada'}), 404
    
    db.session.delete(cita)
    db.session.commit()
    
    return jsonify({'mensaje': 'Cita eliminada correctamente'}), 200


# ==================== RUTAS GENERALES ====================


@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health():
    if request.method == 'OPTIONS':
        return '', 200
    return jsonify({'status': 'API activa'}), 200


@app.route('/api/health/pool', methods=['GET', 'OPTIONS'])
def health_pool():
    """Monitorea el estado del connection pool"""
    if request.method == 'OPTIONS':
        return '', 200
    try:
        db.session.execute(db.text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'pool_type': 'NullPool',
            'message': 'Base de datos accesible'
        }), 200
    except Exception as e:
        print(f"🔴 ERROR en health_pool: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/api/init-data', methods=['GET', 'POST', 'OPTIONS'])
def init_data():
    """Endpoint para inicializar datos de prueba"""
    if request.method == 'OPTIONS':
        return '', 200
    try:
        # Limpiar datos viejos EN EL ORDEN CORRECTO (respetando foreign keys)
        Cita.query.delete()
        Barbero.query.delete()
        Servicio.query.delete()
        Cliente.query.delete()
        db.session.commit()
        print("✅ Datos viejos eliminados")
        
        # Crear barberos
        barberos = [
            Barbero(nombre='Juan Carlos', email='juan@example.com', telefono='1234567890', comision=25.0),
            Barbero(nombre='Pedro López', email='pedro@example.com', telefono='0987654321', comision=20.0),
            Barbero(nombre='Miguel Ruiz', email='miguel@example.com', telefono='1122334455', comision=22.0),
        ]
        db.session.add_all(barberos)
        db.session.commit()
        print("✅ Barberos creados")
        
        # Crear servicios
        servicios = [
            Servicio(nombre='Corte de Cabello', precio=15.00, descripcion='Corte clásico'),
            Servicio(nombre='Barba', precio=10.00, descripcion='Afeitado profesional'),
            Servicio(nombre='Corte + Barba', precio=23.00, descripcion='Combo completo'),
            Servicio(nombre='Líneas', precio=8.00, descripcion='Líneas de precisión'),
        ]
        db.session.add_all(servicios)
        db.session.commit()
        print("✅ Servicios creados")
        
        return jsonify({
            'mensaje': 'Datos inicializados correctamente',
            'barberos': Barbero.query.count(),
            'servicios': Servicio.query.count()
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ==================== INICIALIZAR BD ====================


with app.app_context():
    db.create_all()
    print("✅ Base de datos inicializada")
    
    # Verificar y crear admin
    admin_email = 'Rodritapia92@gmail.com'
    admin_user = Usuario.query.filter_by(email=admin_email).first()
    
    if not admin_user:
        admin_user = Usuario(
            email=admin_email,
            nombre='Administrador',
            rol='admin'
        )
        admin_user.set_password('rodritapia924321')
        db.session.add(admin_user)
        db.session.commit()
        print("✅ Admin creado")
    else:
        if admin_user.rol != 'admin':
            admin_user.rol = 'admin'
            db.session.commit()
            print(f"✅ Rol de {admin_email} actualizado a 'admin'")
        else:
            print(f"✅ Admin {admin_email} verificado")
    
    # Crear barberos si no existen
    if Barbero.query.count() == 0:
        barberos = [
            Barbero(nombre='Juan Carlos', email='juan@example.com', telefono='1234567890', comision=25.0),
            Barbero(nombre='Pedro López', email='pedro@example.com', telefono='0987654321', comision=20.0),
            Barbero(nombre='Miguel Ruiz', email='miguel@example.com', telefono='1122334455', comision=22.0),
        ]
        db.session.add_all(barberos)
        db.session.commit()
        print("✅ Barberos creados")
    else:
        print(f"ℹ️ {Barbero.query.count()} barberos ya existen")
    
    # Crear servicios si no existen
    if Servicio.query.count() == 0:
        servicios = [
            Servicio(nombre='Corte de Cabello', precio=15.00, descripcion='Corte clásico'),
            Servicio(nombre='Barba', precio=10.00, descripcion='Afeitado profesional'),
            Servicio(nombre='Corte + Barba', precio=23.00, descripcion='Combo completo'),
            Servicio(nombre='Líneas', precio=8.00, descripcion='Líneas de precisión'),
        ]
        db.session.add_all(servicios)
        db.session.commit()
        print("✅ Servicios creados")
    else:
        print(f"ℹ️ {Servicio.query.count()} servicios ya existen")


if __name__ == '__main__':
    app.run(debug=True)