from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from config import Config

db            = SQLAlchemy()
login_manager = LoginManager()
mail          = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    login_manager.login_view = 'auth.login'

    from app.campaigns.routes import campaigns_bp
    from app.tracker.routes   import tracker_bp
    from app.training.routes  import training_bp
    from app.auth             import auth_bp
    from app.reports.routes   import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(campaigns_bp, url_prefix='/campaigns')
    app.register_blueprint(tracker_bp)
    app.register_blueprint(training_bp)
    app.register_blueprint(reports_bp)

    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    return app
