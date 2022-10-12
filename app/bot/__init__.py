import datetime
import logging

from app.bot.todo import TodoManager
from app.routes.config import LOGGER_CONFIG
from app.bot.user import UserManager


class Bot():
    def __init__(self, api, data):
        logger = logging.getLogger(LOGGER_CONFIG['NAME'])
        self.api = api
        logger.debug("Validate User")
        userobject = UserManager(self.api, data=data)
        if userobject.user:
            username = [x for x in userobject.user][0]
            self.user = userobject.user[username]
        else:
            self.user = None
        self.valid_user = True if userobject else False
        self.is_admin = True if self.user['ismanager'] else False
        self.is_manager = True if self.user['ismanager'] else False
        self.data = data
        logger.debug("Validated User")

        self.supported_commands = {
            'add task': self.add_task,
            'remove task': self.remove_task,
            'list tasks': self.list_tasks,
            'modify task': self.modify_task,
            'help': self.help,
            'about': self.about,
            'show version': self.show_version_number
        }
        logger.debug('supported commands:\n' + str(self.supported_commands.keys()))

        self.supported_admin_commands = {
            'add user': self.add_user,
            'delete user': self.delete_user,
            'modify user': self.modify_user,
        }

        self.manager_commands = {
            'add task to reportees': self.add_task_to_reportees,
            'list tasks from reportees': self.list_tasks_from_reportees,
            'remove task from reportees': self.remove_task_from_reportees,
            'modify task from reportees': self.modify_task_from_reportees
        }

    def data_handler(self, data):
        message = self.api.messages.get(data['id']).text
        func = None
        for i, command in enumerate(self.supported_commands):
            if message.startswith(command):
                func = command

        if func:
            self.supported_commands[func](data, message)
            return

        for i, command in enumerate(self.manager_commands):
            if message.startswith(command):
                priv = self.validate_manager(data)
                if not priv:
                    return
                func = command
        if func:
            self.manager_commands[func](data, message)
            return

        for i, command in enumerate(self.supported_admin_commands):
            if message.startswith(command):
                priv = self.validate_admin(data)
                if not priv:
                    return
                func = command
        if func:
            self.supported_admin_commands[func](data, message)

        if not func:
            self.api.messages.create(text="Not a valid command. Please see help for supported commands",
                                     roomId=self.data['roomId'])

    def validate_manager(self, data):
        if not self.is_manager:
            self.api.messages.create(files=['app/reject.gif'],
                                     roomId=data['roomId'],
                                     parentId=data['id'],
                                     text='You dont have authorization to run this command')
            return False
        else:
            return True

    def validate_admin(self, data):
        if not self.is_admin:
            self.api.messages.create(files=['app/reject.gif'],
                                     roomId=data['roomId'],
                                     parentId=data['id'],
                                     text='You dont have authorization to run this command')
            return False
        else:
            return True

    def add_task(self, data, message):
        # add task task=name; priority=low; state=initial;
        task_data = message.split('add task')[1]
        if not task_data:
            self.send_message(
                "Valid parameters not passed to the command. Please refer to help to see how to use the commands")
            return
        try:
            task_data = {a.split('=')[0].strip(): a.split('=')[1].strip() for a in task_data.split(';')}
        except IndexError:
            self.send_message(
                "Valid parameters not passed to the command. Please refer to help to see how to use the commands")
            return

        task_data['message_id'] = data['id']
        required = ['task', 'priority', 'state', 'task_id', 'due']
        valid_task = all([x in task_data for x in required])
        if not valid_task:
            self.send_message(
                "Valid parameters not passed to the command. Please refer to help to see how to use the commands")
            return

        try:
            duedate = datetime.datetime.strptime(task_data['due'], "%d/%m/%y %H:%M:%S")
        except ValueError:
            self.send_message(
                "Invalid date format for due date. Please specify the due date in following format: dd/mm/yy HH:MM:SS")
            return

        task_data['due'] = duedate
        tasks_object = TodoManager(self.user)
        task_ids = [x['taskid'] for x in tasks_object.tasks]
        if self.user['username'] + '_' + task_data['task_id'] in task_ids:
            self.send_message(f"Task id {task_data['task_id']} already exists, please choose a unique task id")
            return

        tasks_object.add_task(task_data, owner=self.user['username'], submitter=self.user['username'])
        self.send_message(f"Task `{task_data['task']}` added successfully")

    def add_task_to_reportees(self, data, message):
        pass

    def remove_task(self, data, message):
        pass

    def list_tasks(self, data, message):
        tasks_object = TodoManager(self.user)
        self_tasks, manager_tasks = tasks_object._get_markdown_table(self.api, data)
        self_text = 'Your tasks:\n```\n'+self_tasks+'\n```' if self_tasks else "No tasks exist"
        man_text = f'\n\nManager assigned tasks:\n```\n'+manager_tasks+'\n```' if manager_tasks else ""
        self.api.messages.create(markdown=self_text+man_text,
                                 roomId=self.data['roomId'])

    def modify_task(self, data, message):
        pass

    def list_tasks_from_reportees(self, data, message):
        pass

    def help(self):
        pass

    def about(self):
        pass

    def show_version_number(self):
        pass

    def add_user(self, data, message):
        pass

    def delete_user(self, data, message):
        pass

    def modify_user(self, data, message):
        pass

    def remove_task_from_reportees(self, data, message):
        pass

    def modify_task_from_reportees(self, data, message):
        pass

    def send_message(self, text):
        self.api.messages.create(text=text, roomId=self.data['roomId'])