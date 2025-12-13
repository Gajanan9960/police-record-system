from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from app.config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
mail = Mail()
migrate = Migrate()
csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # Register Blueprints
    from app.auth import auth as auth_bp
    app.register_blueprint(auth_bp)
    
    from app.cases import cases as cases_bp
    app.register_blueprint(cases_bp)
    
    from app.dashboard import dashboard as dashboard_bp
    app.register_blueprint(dashboard_bp)

    from app.criminals import criminals as criminals_bp
    app.register_blueprint(criminals_bp)

    from app.main import main as main_bp
    app.register_blueprint(main_bp)
    
    from app.clerk import clerk as clerk_blueprint
    app.register_blueprint(clerk_blueprint)
    
    from app.io import io as io_blueprint
    app.register_blueprint(io_blueprint)
    
    from app.malkhana import malkhana as malkhana_blueprint
    app.register_blueprint(malkhana_blueprint)
    
    from app.forensic import forensic as forensic_blueprint
    app.register_blueprint(forensic_blueprint)
    
    from app.court import court as court_blueprint
    app.register_blueprint(court_blueprint)

    from app.admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint)

    from app.tasks import tasks as tasks_blueprint
    app.register_blueprint(tasks_blueprint)

    from app.search import search as search_blueprint
    app.register_blueprint(search_blueprint)
    
    return app
