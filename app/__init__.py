from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)

    login.login_view = 'auth.login'
    login.login_message = 'Please log in to access this page.'
    login.login_message_category = 'info'

    from .auth import auth as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from .main import main as main_bp
    app.register_blueprint(main_bp)

    return app