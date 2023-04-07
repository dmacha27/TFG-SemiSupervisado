import os
import re
import sys

from flask import Flask, request
from flask_babel import Babel
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix

db = SQLAlchemy()
DB_NAME = "db.db"


def create_app():
    app = Flask(__name__,
                static_url_path='',
                static_folder='./static',
                )
    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
    )
    app.secret_key = "ae4c977b14e2ecf38d485869018ec8f924b312132ee3d11d1ce755cdff9bc0af"
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config.update(SESSION_COOKIE_SAMESITE='Strict')
    app.config['CARPETA_DATASETS'] = os.path.join(os.path.basename(os.path.dirname(__file__)), 'datasets')
    app.config['SESSION_TYPE'] = 'filesystem'
    db.init_app(app)

    def get_locale():
        return request.accept_languages.best_match(['es', 'en'])

    babel = Babel(app, locale_selector=get_locale)

    @app.context_processor
    def variables_globales():
        return {'titulos': {'selftraining': 'Self-Training',
                            'cotraining': 'Co-Training',
                            'democraticcolearning': 'Democratic Co-Learning',
                            'tritraining': 'Tri-Training'}}

    @app.template_filter()
    def nombredataset(text):
        """Obtiene solo el nombre del conjunto de datos
        eliminando la ruta completa"""

        return os.path.split(re.split(r"-", text)[0])[1]

    from .main_routes import main_bp
    from .configuration_routes import configuration_bp
    from .visualization_routes import visualization_bp
    from .data_routes import data_bp

    app.register_blueprint(main_bp, url_prefix='/')
    app.register_blueprint(configuration_bp, url_prefix='/configuracion')
    app.register_blueprint(visualization_bp, url_prefix='/visualizacion')
    app.register_blueprint(data_bp, url_prefix='/datos')

    from .models import User

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(email):
        return User.query.filter_by(email=email).first()

    return app
