from app.db import db
from marshmallow import Schema, fields
from flask import current_app as app


class UserSchema(Schema):
    user_id = fields.String(required=True)
    manager_id = fields.String(required=True)
    ismanager = fields.Boolean(required=True)
    # when user is deleted, dtime value is updated with timestamp. if none, user is active
    dtime = fields.DateTime(dump_default=None, allow_none=True)
    mtime = fields.DateTime(dump_default=None)

    # class Meta:
    #     fields = ("url",)


class BulkCreateUserSchema(Schema):
    user_list = fields.List(fields.String(), required=True)


# Create User schema in user table
# Table will be initialised when app is started
# Refer app.__init__.py - db.create_all()
class User(db.Model):
    __tablename__ = 'user'
    __schema__ = UserSchema
    username = db.Column(db.String(25), primary_key=True)
    manager_id = db.Column(db.String(25), default=None)
    ismanager = db.Column(db.Boolean, default=False)
    dtime = db.Column(db.DateTime, default=None)
    mtime = db.Column(db.DateTime, default=None)

    @classmethod
    def fetch_user(cls, username):
        # Query database for the given user
        fetch = app.session.query(User.username, User.manager_id, User.ismanager).filter(
            User.username == username,
            User.dtime.is_(None)
        ).all()

        users = {}
        for user in fetch:
            user = user._asdict()
            users[user['username']] = user

        return users
