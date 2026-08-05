from flask import Flask, render_template, jsonify
from dotenv import load_dotenv
import pytesseract

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)
import os

from utils import (
    login_required,
    current_user
)

from routes_auth import auth_bp
from  routes_dashboard import dashboard_bp
from  routes_alerts import alerts_bp
from  routes_users import users_bp
from  routes_employees import employees_bp
from  routes_documents import documents_bp
from  routes_clients import clients_bp
from  routes_stock import stock_bp
from  routes_maintenance import maintenance_bp
from  routes_ocr import ocr_bp
from  routes_signatures import signatures_bp
from  routes_agenda import agenda_bp

load_dotenv()


def create_app():

    app = Flask(__name__)

    # ==========================
    # CONFIGURATION
    # ==========================

    app.config["SECRET_KEY"] = os.getenv(
        "SECRET_KEY",
        "aerodoc-dev-secret-change-me"
    )

    app.config["DB_HOST"] = os.getenv(
        "DB_HOST",
        "localhost"
    )

    app.config["DB_USER"] = os.getenv(
        "DB_USER",
        "root"
    )

    app.config["DB_PASSWORD"] = os.getenv(
        "DB_PASSWORD",
        ""
    )

    app.config["DB_NAME"] = os.getenv(
        "DB_NAME",
        "aerodoc"
    )

    app.config["UPLOAD_FOLDER"] = os.getenv(
        "UPLOAD_FOLDER",
        "uploads"
    )

    app.config["SIGNED_FOLDER"] = os.getenv(
        "SIGNED_FOLDER",
        "documents_signes"
    )

    app.config["SIGNATURE_FOLDER"] = os.getenv(
        "SIGNATURE_FOLDER",
        "signatures"
    )

    app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024

    # ==========================
    # DOSSIERS
    # ==========================

    os.makedirs(
        app.config["UPLOAD_FOLDER"],
        exist_ok=True
    )

    os.makedirs(
        app.config["SIGNED_FOLDER"],
        exist_ok=True
    )

    os.makedirs(
        app.config["SIGNATURE_FOLDER"],
        exist_ok=True
    )

    os.makedirs(
        os.path.join(
            app.config["UPLOAD_FOLDER"],
            "documents"
        ),
        exist_ok=True
    )

    os.makedirs(
        os.path.join(
            app.config["UPLOAD_FOLDER"],
            "ocr"
        ),
        exist_ok=True
    )

    # ==========================
    # BLUEPRINTS
    # ==========================

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(alerts_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(employees_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(stock_bp)
    app.register_blueprint(maintenance_bp)
    app.register_blueprint(ocr_bp)
    app.register_blueprint(signatures_bp)
    app.register_blueprint(agenda_bp)

    # ==========================
    # CONTEXT USER
    # ==========================

    @app.context_processor
    def inject_user():
        return {
            "current_user": current_user()
        }

    # ==========================
    # ROUTES PAGES
    # ==========================

    @app.route("/")
    @login_required
    def index():
        return render_template("index.html")

    @app.route("/api/me")
    @login_required
    def api_me():

        user = current_user()

        if not user:
            return jsonify({
                "error": "Utilisateur introuvable"
            }), 404

        user.pop(
            "mot_de_passe",
            None
        )

        return jsonify(user)

    # ==========================
    # HEALTH CHECK
    # ==========================

    @app.route("/api/health")
    def health():

        return jsonify({
            "success": True,
            "message": "AeroDoc API opérationnelle"
        })

    return app


app = create_app()


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )