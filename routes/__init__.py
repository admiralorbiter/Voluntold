from .auth import auth_bp
from .main import main_bp
from .dashboard import dashboard_bp
from .upcoming_events import upcoming_events_bp
from .dia import dia_events_bp

def init_routes(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(upcoming_events_bp, url_prefix='/events')
    app.register_blueprint(dia_events_bp, url_prefix='/events') 