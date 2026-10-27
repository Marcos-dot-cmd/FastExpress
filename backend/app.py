"""API REST y entrega de los archivos estáticos del frontend."""
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory
from werkzeug.exceptions import BadRequest, UnsupportedMediaType
from backend.service import quote, ValidationError

FRONTEND = Path(__file__).resolve().parents[1] / "frontend"

def create_app():
    app = Flask(__name__, static_folder=None)
    app.config["MAX_CONTENT_LENGTH"] = 16384

    @app.get("/")
    def index():
        return send_from_directory(FRONTEND, "index.html")

    @app.get("/assets/<path:filename>")
    def asset(filename):
        return send_from_directory(FRONTEND, filename)

    @app.get("/api/health")
    def health():
        return jsonify(status="ok", servicio="FastExpress")

    @app.post("/api/cotizaciones")
    def cotizar():
        try:
            data = request.get_json()
        except (BadRequest, UnsupportedMediaType):
            return jsonify(error="Envíe JSON válido con Content-Type application/json."), 400
        try:
            result = quote(data)
        except ValidationError as exc:
            return jsonify(error=str(exc)), 400
        return jsonify(result), 200

    @app.errorhandler(413)
    def too_large(error):
        return jsonify(error="Solicitud demasiado grande."), 413

    return app
