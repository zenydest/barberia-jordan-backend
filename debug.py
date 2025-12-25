from app import create_app

app = create_app()

# Debug: Ver todas las rutas registradas
print("\n=== RUTAS REGISTRADAS EN FLASK ===")
for rule in app.url_map.iter_rules():
    print(f"{rule.rule:40} -> {rule.endpoint}")

print("\n=== PROBANDO CONEXIÓN CON DB ===")
try:
    with app.app_context():
        from app.models import Cliente
        print(f"✅ Modelos importados correctamente")
        print(f"✅ Base de datos SQLite lista")
except Exception as e:
    print(f"❌ Error importando modelos: {e}")