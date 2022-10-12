import sqlalchemy
from flask import Flask
from app.db import db, migrate
from app.db import config
from flask_sqlalchemy_session import flask_scoped_session
from sqlalchemy.orm import sessionmaker
from app.routes import userbp as route_bp
from app.routes import todobp
from app.routes import handlerbp

# Flask Application Factory
def create_app():
    flask_app = Flask(__name__)
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_CONNECTION_URI
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Connect to database
    engine = sqlalchemy.create_engine(config.DATABASE_CONNECTION_URI)
    session_factory = sessionmaker(bind=engine)
    _scoped_session = flask_scoped_session(session_factory, flask_app)
    flask_app.session = _scoped_session
    flask_app.app_context().push()

    # Initialise database
    db.init_app(flask_app)
    db.create_all()

    # Support for migrations
    migrate.init_app(flask_app, db)

    # Register the routes blueprint
    flask_app.register_blueprint(route_bp)
    flask_app.register_blueprint(todobp)
    flask_app.register_blueprint(handlerbp)

    return flask_app