from .auth import auth_bp
from .main import main_bp
from .dashboard import dashboard_bp
from .upcoming_events import upcoming_events_bp
from .dia import dia_events_bp
from .school_mappings import bp as school_mappings_bp
from .district import bp as district_bp

__all__ = ['init_routes']

def init_routes(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(upcoming_events_bp, url_prefix='/events')
    app.register_blueprint(dia_events_bp, url_prefix='/events')
    app.register_blueprint(school_mappings_bp) 
    app.register_blueprint(district_bp)