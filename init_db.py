from app import app, db, Usuario

with app.app_context():
    # Crear todas las tablas
    db.create_all()
    print("✅ Tablas creadas en PostgreSQL")
    
    # Crear admin si no existe
    if not Usuario.query.filter_by(email='Rodritapia92@gmail.com').first():
        admin = Usuario(
            email='Rodritapia92@gmail.com',
            nombre='Administrador',
            rol='admin'
        )
        admin.set_password('rodritapia924321')
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin creado: Rodritapia92@gmail.com")
    else:
        print("ℹ️ Admin ya existe")
