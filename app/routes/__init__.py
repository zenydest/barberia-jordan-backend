def register_routes(app):
    from . import clientes, barberos, servicios, cobros, exportar, reportes
    
    # Rutas de clientes
    app.route('/api/clientes', methods=['GET'])(clientes.get_clientes)
    app.route('/api/clientes/<int:id>', methods=['GET'])(clientes.get_cliente)
    app.route('/api/clientes', methods=['POST'])(clientes.create_cliente)
    app.route('/api/clientes/<int:id>', methods=['PUT'])(clientes.update_cliente)
    app.route('/api/clientes/<int:id>', methods=['DELETE'])(clientes.delete_cliente)
    
    # Rutas de barberos
    app.route('/api/barberos', methods=['GET'])(barberos.get_barberos)
    app.route('/api/barberos/<int:id>', methods=['GET'])(barberos.get_barbero)
    app.route('/api/barberos', methods=['POST'])(barberos.create_barbero)
    app.route('/api/barberos/<int:id>', methods=['PUT'])(barberos.update_barbero)
    app.route('/api/barberos/<int:id>', methods=['DELETE'])(barberos.delete_barbero)
    
    # Rutas de servicios
    app.route('/api/servicios', methods=['GET'])(servicios.get_servicios)
    app.route('/api/servicios/<int:id>', methods=['GET'])(servicios.get_servicio)
    app.route('/api/servicios', methods=['POST'])(servicios.create_servicio)
    app.route('/api/servicios/<int:id>', methods=['PUT'])(servicios.update_servicio)
    app.route('/api/servicios/<int:id>', methods=['DELETE'])(servicios.delete_servicio)
    
    # Rutas de cobros
    app.route('/api/cobros', methods=['GET'])(cobros.get_cobros)
    app.route('/api/cobros/<int:id>', methods=['GET'])(cobros.get_cobro)
    app.route('/api/cobros', methods=['POST'])(cobros.create_cobro)
    app.route('/api/cobros/<int:id>', methods=['PUT'])(cobros.update_cobro)
    app.route('/api/cobros/<int:id>', methods=['DELETE'])(cobros.delete_cobro)
    
    # Rutas de reportes ← AGREGAR ESTO
    app.route('/api/reportes/diario', methods=['GET'])(reportes.reporte_diario)
    app.route('/api/reportes/semanal', methods=['GET'])(reportes.reporte_semanal)
    app.route('/api/reportes/mensual', methods=['GET'])(reportes.reporte_mensual)
    app.route('/api/reportes/anual', methods=['GET'])(reportes.reporte_anual)
    app.route('/api/reportes/servicios-vendidos', methods=['GET'])(reportes.servicios_mas_vendidos)
    app.route('/api/reportes/rango', methods=['GET'])(reportes.reporte_rango_fechas)
    
    # Ruta de exportar
    app.route('/api/exportar/generar', methods=['GET'])(exportar.generar_reporte)
