from datetime import datetime
from sqlalchemy import exc
from app.db.models.todo import Todo
from flask import current_app as app
from tabulate import tabulate

class TodoManager:
    def __init__(self, user):
        self.user = user
        self.tasks = Todo.fetch_tasks(user['username'])
        self.user_tasks = [x for x in self.tasks if x['submitter'] == user['username']]
        self.manager_tasks = [x for x in self.tasks if x['submitter'] != user['username']]
        self.column_names = [
            'TASK ID',
            'TASK NAME',
            'PRIORITY',
            'STATE',
            'TIME CREATED',
            'TIME DUE',
            'TIMES MODIFIED',
        ]

    def add_task(self, task, owner, submitter):
        newdata = Todo(owner=owner, submitter=submitter, todo_item=task['task'],
                       priority=task['priority'], state=task['state'], taskid=f'{submitter}_{task["task_id"]}',
                       createtime=datetime.now(), duetime=task['due'],
                       mtime=datetime.now(), timesmodified=0)

        app.session.add(newdata)

        try:
            app.session.commit()
        # If there is any exception during commit, the session should rollback
        except exc.IntegrityError:
            app.session.rollback()
        except Exception as e:
            app.session.rollback()

    def _get_markdown_table(self, api, data):
        tasks = Todo._fetch_all_where(Todo.owner == self.user['username'], excluded_fields=['mtime', 'id'])
        self_tasks = [x for x in tasks if x['owner'] == x['submitter']]
        manager_tasks = [x for x in tasks if x not in self_tasks]

        for x in self_tasks:
            del x['owner']
            del x['submitter']
            x['priority'] = x['priority'].name
            x['state'] = x['state'].name

        for x in manager_tasks:
            del x['owner']
            del x['submitter']
            x['priority'] = x['priority'].name
            x['state'] = x['state'].name

        self_task_table = tabulate(self_tasks, headers='keys', tablefmt="github")
        manager_task_table = tabulate(manager_tasks, headers='keys', tablefmt="github")
        return self_task_table, manager_task_table

