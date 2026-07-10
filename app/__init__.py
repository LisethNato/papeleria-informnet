from flask import Flask, render_template

from config import Config
from app.extensions import db, migrate, login_manager


def create_app(config_class=Config):

    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Por favor inicia sesión para continuar."

    from app.models import Producto, Cliente, Usuario, Venta, DetalleVenta

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    from app.routes.main import main
    from app.routes.auth import auth
    from app.routes.productos import productos
    from app.routes.clientes import clientes
    from app.routes.ventas import ventas
    from app.routes.usuarios import usuarios

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(productos)
    app.register_blueprint(clientes)
    app.register_blueprint(ventas)
    app.register_blueprint(usuarios)

    @app.errorhandler(403)
    def acceso_denegado(e):
        return render_template("403.html"), 403

    return app