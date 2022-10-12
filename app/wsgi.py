from app import create_app


# Create the app from application factory.
# This should be the only instance where app should be created
# and serves as an entrypoint to the application
# All other modules should import app from flask.current_app
app = create_app()
