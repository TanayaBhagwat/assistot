from webargs.flaskparser import use_kwargs

from app.routes import userbp
from flask import current_app as app
from app.db.models.user import User, UserSchema, BulkCreateUserSchema
from flask import json, request
from datetime import datetime
from sqlalchemy import or_, exc

#
# userbp blueprint created in  routes/__init__.py and registered to app in application factory
@userbp.get('/<username>')
def get_user(username):
    # Query database for the given user
    return User.fetch_user(username)

