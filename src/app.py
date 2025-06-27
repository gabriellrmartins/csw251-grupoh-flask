from flask import Flask
from src.repositories.building_repository import BuildingRepository
import click
from src.repositories.room_repository import RoomRepository
from src.services.building_service import BuildingService
from src.services.room_service import RoomService
from src.controllers.building_controller import BuildingController
from src.controllers.room_controller import RoomController
from src.models.building_model import Building
from src.models.room_model import Room
from src.utils.shared.db.base import Base, db


def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://postgres:postgres@sarc-db-instance.cuqc68zbmxj1.us-east-1.rds.amazonaws.com:5432/sarcdb"
    db.init_app(app)

    # The app context is needed for db.session to be available
    with app.app_context():
        # Inject repositories using the current db.session
        app.building_repository = BuildingRepository(db.session)
        app.room_repository = RoomRepository(db.session)
        # Inject services using the repositories
        app.building_service = BuildingService(app.building_repository)
        app.room_service = RoomService(app.room_repository)
        # Inject controllers using the services
        app.building_controller = BuildingController(app.building_service)
        app.room_controller = RoomController(app.room_service)

        # Register routes for building and room controllers
        app.register_blueprint(app.building_controller.blueprint)
        app.register_blueprint(app.room_controller.blueprint)

    @app.route('/')
    def health_check():
        return {'message': 'Alive!'}, 200

    # Add a new CLI command for database initialization
    @app.cli.command("init-db")
    def init_db_command():
        """Clear existing data and create new tables."""
        db.create_all()
        click.echo("Initialized the database.")

    return app