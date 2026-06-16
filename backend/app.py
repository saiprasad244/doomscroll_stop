import os
import sys
# Add project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from backend.database.connection import init_db

# Import blueprints
from backend.routes.auth import auth_bp
from backend.routes.usage import usage_bp
from backend.routes.predict import predict_bp
from backend.routes.dashboard import dashboard_bp
from backend.routes.achievements import achievements_bp
from backend.routes.mood import mood_bp
from backend.routes.reports import reports_bp
from backend.routes.leaderboard import leaderboard_bp
from backend.routes.focus import focus_bp

def create_app():
    app = Flask(__name__)
    
    # Configure CORS
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # Configure JWT
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "doomscroll-shield-super-secret-key-999")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 86400 # 24 hours
    jwt = JWTManager(app)
    
    # Register error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"message": "The token has expired.", "error": "token_expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"message": "Signature verification failed.", "error": "invalid_token"}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({"message": "Request does not contain an access token.", "error": "authorization_required"}), 401

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(usage_bp, url_prefix="/api")
    app.register_blueprint(predict_bp, url_prefix="/api")
    app.register_blueprint(dashboard_bp, url_prefix="/api")
    app.register_blueprint(achievements_bp, url_prefix="/api")
    app.register_blueprint(mood_bp, url_prefix="/api")
    app.register_blueprint(reports_bp, url_prefix="/api")
    app.register_blueprint(leaderboard_bp, url_prefix="/api")
    app.register_blueprint(focus_bp, url_prefix="/api")
    
    # Initialize DB tables
    init_db()
    
    @app.route("/")
    def index():
        return jsonify({
            "status": "online",
            "message": "DoomScroll Shield Backend API is running.",
            "version": "1.0.0"
        })
        
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
