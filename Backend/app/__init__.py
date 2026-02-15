from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.config import Config

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['CORS_HEADERS'] = 'Content-Type,Authorization'

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)

    # JWT error handlers
    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        from flask import jsonify
        return jsonify({
            'error': 'Missing Authorization Header',
            'message': 'Request does not contain a valid token'
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(callback):
        from flask import jsonify
        return jsonify({
            'error': 'Invalid token',
            'message': 'Token verification failed'
        }), 422

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        from flask import jsonify
        return jsonify({
            'error': 'Token has expired',
            'message': 'Please login again'
        }), 401

    # CORS - allow all
    CORS(
        app,
        resources={r"/api/*": {"origins": ["http://154.17.17.210", "http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173", "http://127.0.0.1:3000"]}},
        supports_credentials=False,
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-Requested-With"]
    )

    # Initialize R2 storage
    from app.utils.r2_storage import r2_storage
    r2_storage.init_app(app)

    # Register blueprints
    from app.routes import auth, products, stores, orders, customers, employees, inventory, upload, stats
    app.register_blueprint(auth.bp)
    app.register_blueprint(products.bp)
    app.register_blueprint(stores.bp)
    app.register_blueprint(orders.bp)
    app.register_blueprint(customers.bp)
    app.register_blueprint(employees.bp)
    app.register_blueprint(inventory.bp)
    app.register_blueprint(upload.bp)
    app.register_blueprint(stats.stats_bp)

    return app
