from app import app, db

with app.app_context():
    print("🔄 Creando tablas...")
    db.create_all()
    print("✅ Tablas creadas exitosamente!")
