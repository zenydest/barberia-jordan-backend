from app import app, db, Usuario

# Inicializar BD al cargar
with app.app_context():
    print("🔄 Inicializando PostgreSQL...")
    db.create_all()
    print("✅ Tablas creadas/verificadas")
    
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
        print("✅ Admin creado")
    else:
        print("ℹ️ Admin ya existe")

if __name__ == '__main__':
    app.run()
