from webargs.flaskparser import use_kwargs

from app.routes import todobp
from flask import current_app as app
from app.db.models.todo import TodoSchema, Todo
from flask import json, request
from datetime import datetime
from sqlalchemy import or_, exc

#
# bp blueprint created in  routes/__init__.py and registered to app in application factory
@todobp.get('/api/1/task/<task_id>/')
def get_task(task_id):
    """
    GET request to check if given hostname:port/path is a malware
    The query sets is_safe = True in the response if given url is a malware
    otherwise is_safe is set to False
    :param _hostname_port: hostname and port for the query url
    :param _path_query: path of the query url
    :return:
        200: json: {"data": {"url": str}, "is_safe": bool}
    """

    # Query database for the given user
    fetch = app.session.query(Todo).filter(
        Todo.taskid == f"{task_id}/",
        Todo.dtime.is_(None)
    ).all()

    # data = {'url': f"{_hostname_port}/{_path_query}"}

    return f"{json.dumps(fetch)}", 200
