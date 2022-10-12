from datetime import datetime
import json
from app.db.models.user import User
from flask import current_app as app
from sqlalchemy import or_, exc

class UserManager:

    def __init__(self, api, data):
        self.user = User.fetch_user(data['personEmail'].split('@')[0])
        # if not self.user:
        #     person = api.people.get(data['personId'])
        #     manager = api.people.get(person.managerId)
        #     manager = manager.userName.split('@')[0]
        #     newdata = User(username=data['personEmail'].split('@')[0], manager_id=manager, mtime=datetime.now())
        #     app.session.add(newdata)
        #     try:
        #         app.session.commit()
        #
        #     # If there is any exception during commit, the session should rollback
        #     except exc.IntegrityError:
        #         app.session.rollback()
        #     except Exception as e:
        #         app.session.rollback()
