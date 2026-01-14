# seed_db.py
from app import app, db, Barbero, Servicio

with app.app_context():
    # Crear barberos
    barberos = [
        Barbero(nombre='Juan Carlos', email='juan@example.com', telefono='1234567890', comision=25.0),
        Barbero(nombre='Pedro López', email='pedro@example.com', telefono='0987654321', comision=20.0),
        Barbero(nombre='Miguel Ruiz', email='miguel@example.com', telefono='1122334455', comision=22.0),
    ]
    
    servicios = [
        Servicio(nombre='Corte de Cabello', precio=15.00, descripcion='Corte clásico'),
        Servicio(nombre='Barba', precio=10.00, descripcion='Afeitado profesional'),
        Servicio(nombre='Corte + Barba', precio=23.00, descripcion='Combo completo'),
        Servicio(nombre='Líneas', precio=8.00, descripcion='Líneas de precisión'),
    ]
    
    db.session.add_all(barberos + servicios)
    db.session.commit()
    
    print("✅ Datos de prueba agregados")
