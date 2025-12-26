from flask import Blueprint

from .barberos import get_barberos_bp
from .servicios import get_servicios_bp
from .cobros import get_cobros_bp
from .clientes import get_clientes_bp
from .reportes import get_reportes_bp
from .exportar import get_exportar_bp

barberos_bp = get_barberos_bp()
servicios_bp = get_servicios_bp()
cobros_bp = get_cobros_bp()
clientes_bp = get_clientes_bp()
reportes_bp = get_reportes_bp()
exportar_bp = get_exportar_bp()

__all__ = ['barberos_bp', 'servicios_bp', 'cobros_bp', 'clientes_bp', 'reportes_bp', 'exportar_bp']

