import flask_sqlalchemy
from flask_migrate import Migrate
db = flask_sqlalchemy.SQLAlchemy()

# Create the migrate object
# Database schema backup can be created by running 'flask run'
migrate = Migrate()
