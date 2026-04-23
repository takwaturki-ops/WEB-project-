from flask import Flask
from flask_cors import CORS
from .database import close_db

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config.from_mapping(
        SECRET_KEY='dev-change-in-prod',
        DATABASE='sac_shop.db',
        DEBUG=True
    )

    app.teardown_appcontext(close_db)

    from .routes.products import products_bp
    from .routes.auth import auth_bp
    from .routes.orders import orders_bp

    app.register_blueprint(products_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(orders_bp, url_prefix='/api')

    return app