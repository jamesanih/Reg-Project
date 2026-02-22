from flask import Flask
from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    from app.routes import main_bp
    app.register_blueprint(main_bp)

    # Initialize RAG pipeline on first request
    with app.app_context():
        from app.rag.ingest import ensure_index_built
        ensure_index_built(app.config)

    return app
