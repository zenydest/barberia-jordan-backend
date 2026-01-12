#!/bin/bash
python -c "from app import app, db; app.app_context().push(); db.create_all(); from app import Usuario; u = Usuario(email='Rodritapia92@gmail.com', nombre='Administrador', rol='admin'); u.set_password('rodritapia924321'); db.session.add(u); db.session.commit(); print('✅ BD inicializada!')"
