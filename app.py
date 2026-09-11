from flask import Flask, render_template
from flask_migrate import Migrate
from config import Config
from models import db

migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from routes.dashboard import dashboard_bp
    from routes.resources import resources_bp
    from routes.peering import peering_bp
    from routes.arrangements import arrangements_bp
    from routes.providers import providers_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(resources_bp)
    app.register_blueprint(peering_bp)
    app.register_blueprint(arrangements_bp)
    app.register_blueprint(providers_bp)

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    create_app().run(debug=True)