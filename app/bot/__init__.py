import datetime
import logging
import re

from tabulate import tabulate

from app.bot.todo import TodoManager
from app.routes.config import LOGGER_CONFIG
from app.bot.user import UserManager


class Bot():
    def __init__(self, api, data):
        logger = logging.getLogger(LOGGER_CONFIG['NAME'])
        self.api = api
        logger.debug("Validate User")
        user = data['personEmail'].split('@')[0]
        userobject = UserManager(self.api, user)
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
            '^add (?:task|item)': self.add_task,
            '^(?:remove|delete) (?:task|item)': self.remove_task,
            '^list (?:tasks|task|items|item)': self.list_tasks,
            '^(?:modify|change) (?:tasks|task)': self.modify_task,
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
            '^reportees add task': self.add_task_to_reportees,
            '^reportees list tasks': self.list_tasks_from_reportees,
            '^reportees remove task': self.remove_task_from_reportees,
            '^reportees modify task': self.modify_task_from_reportees,
            '^reportees list group task': self.list_group_tasks_from_reportees
        }

    def data_handler(self, data):
        message = self.api.messages.get(data['id']).text
        func = None
        for i, command in enumerate(self.supported_commands):
            pattern = re.search(f'({command})', message)
            pattern = getattr(pattern, 'groups', lambda: None)()
            if pattern and len(pattern) >= 1 and pattern[0]:
                func = command
                break

        if func:
            self.supported_commands[func](data, message)
            return

        for i, command in enumerate(self.manager_commands):
            pattern = re.search(f'({command})', message)
            pattern = getattr(pattern, 'groups', lambda: None)()
            if pattern and len(pattern) >= 1 and pattern[0]:
                priv = self.validate_manager(data)
                if not priv:
                    return
                func = command
                break
        if func:
            self.manager_commands[func](data, message)
            return

        for i, command in enumerate(self.supported_admin_commands):
            pattern = re.search(f'({command})', message)
            pattern = getattr(pattern, 'groups', lambda: None)()
            if pattern and len(pattern) >= 1 and pattern[0]:
                priv = self.validate_admin(data)
                if not priv:
                    return
                func = command
                break
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
        # task_data = message.split('add task')[1]
        task_data = re.sub('^add (?:task|item)\s', '', message)
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
        required = ['task', 'priority', 'task_id']
        valid_task = all([x in task_data for x in required])
        if not valid_task:
            self.send_message(
                "Valid parameters not passed to the command. Please refer to help to see how to use the commands")
            return

        try:
            duedate = datetime.datetime.strptime(task_data['due'], "%d/%m/%y %H:%M:%S"
                                                 ) if task_data.get('due') else None
        except ValueError:
            self.send_message(
                "Invalid date format for due date. Please specify the due date in following format: dd/mm/yy HH:MM:SS")
            return

        task_data['due'] = duedate
        task_data['state'] = task_data.get('state', 'initial')
        tasks_object = TodoManager(self.user)
        task_ids = [x['task_id'] for x in tasks_object.tasks]
        if self.user['username'] + '_' + task_data['task_id'] in task_ids:
            self.send_message(f"Task id {task_data['task_id']} already exists, please choose a unique task id")
            return

        tasks_object.add_task(task_data, owner=self.user['username'], submitter=self.user['username'])
        self.send_message(f"Task `{task_data['task']}` added successfully")

    def add_task_to_reportees(self, data, message):
        task_data = re.sub('^reportees add task\s', '', message)
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
        required = ['task', 'priority', 'task_id']
        valid_task = all([x in task_data for x in required])
        if not valid_task:
            self.send_message(
                "Valid parameters not passed to the command. Please refer to help to see how to use the commands")
            return

        try:
            duedate = datetime.datetime.strptime(task_data['due'], "%d/%m/%y %H:%M:%S") if task_data.get(
                'due') else None
        except ValueError:
            self.send_message(
                "Invalid date format for due date. Please specify the due date in following format: dd/mm/yy HH:MM:SS")
            return

        task_data['due'] = duedate
        task_data['state'] = task_data.get('state', 'initial')
        tasks_object = TodoManager(self.user)
        group_tasks, individual_tasks = tasks_object.get_reportees_tasks()
        task_ids = dict()

        for task in group_tasks:
            if task in task_ids:
                task_data[task].extend(group_tasks[group_tasks[task]['belongs to'].split(',')])
            else:
                task_data[task] = group_tasks[task]['belongs to'].split(',')

        for x in individual_tasks:
            for task in individual_tasks[x]:
                if task['task_id'] in task_ids:
                    task_ids[task['task_id']].append(x)
                else:
                    task_ids[task['task_id']] = [x]

        if task_data['task_id'] in task_ids:
            self.send_message(f"Task id {task_data['task_id']} already exists for "
                              f"{', '.join(task_ids[task_data['task_id']])}, please choose a unique task id")
            return

        task_data['isgroupitem'] = 1
        user = UserManager(self.api, self.user['username'])
        reportees = user.fetch_reportees(self.user['username'])
        tasks_object = TodoManager(self.user)
        for engn in reportees:
            tasks_object.add_task(task_data, owner=engn, submitter=self.user['username'])
        self.send_message(f"Task `{task_data['task']}` added successfully for all reportees")

    def remove_task(self, data, message):
        # task_data = message.split('remove task')[1].strip()
        task_data = re.sub('(?:remove|delete) (?:task|item)\s', '', message)
        if not task_data:
            self.send_message(
                "Invalid input. Specify a task id to delete")
            return
        task_object = TodoManager(self.user)
        result = task_object.delete_task(task_data)
        if result == None:
            self.send_message(f"No task exists with task id: {task_data}")
            return
        if result == False:
            self.send_message(f"Failed to delete task: {task_data}")
        else:
            self.send_message(f"Removed task: {task_data}")

    def list_tasks(self, data, message):
        tasks_object = TodoManager(self.user)
        self_tasks, manager_tasks = tasks_object._get_markdown_table()
        self_text = 'Your tasks:\n```\n'+self_tasks+'\n```' if self_tasks else "No tasks exist"
        man_text = f'\n\nManager assigned tasks:\n```\n'+manager_tasks+'\n```' if manager_tasks else ""
        self.api.messages.create(markdown=self_text+man_text,
                                 roomId=self.data['roomId'])

    def modify_task(self, data, message):
        task_data = re.sub('(?:modify|change) (?:tasks|task)\s', '', message)
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

        required = ['task_id']
        valid_task = all([x in task_data for x in required])
        if not valid_task:
            self.send_message(
                f"Valid parameters not passed to the command. following parameters are required: {', '.join(required)}")
            return

        try:
            duedate = datetime.datetime.strptime(task_data['due'], "%d/%m/%y %H:%M:%S"
                                                 ) if task_data.get('due') else None
        except ValueError:
            self.send_message(
                "Invalid date format for due date. Please specify the due date in following format: dd/mm/yy HH:MM:SS")
            return

        if duedate:
            task_data['due'] = duedate
        task_id = task_data['task_id']
        del task_data['task_id']
        tasks_object = TodoManager(self.user)
        valid_params = all([x in tasks_object.permitted_fields for x in task_data])
        if not valid_params:
            self.send_message(f"Valid parameters were not passed to the command. "
                              f"Permitted keys are: {', '.join(tasks_object.permitted_fields)}")
            return
        task_ids = [x['task_id'] for x in tasks_object.tasks]
        if self.user['username'] + '_' + task_id not in task_ids:
            self.send_message(f"Task id {task_id} does not exist, please run 'list tasks' to see existing tasks")
            return

        tasks_object.modify_task(task_id, task_data)
        self.send_message(f"Task `{task_id}` modified successfully")

    def list_tasks_from_reportees(self, data, message):
        tasks_object = TodoManager(self.user)
        reportees_task, individual_task = tasks_object.get_reportees_tasks()
        message = ""
        if reportees_task:
            message = """### Group tasks\n"""
            group_tab = tabulate(reportees_task.values(), headers='keys', tablefmt="grid")
            message = message + '```\n' + group_tab + '\n```\n'
        else:
            message = """### No Group tasks exist\n"""

        if individual_task:
            message += """### Individual tasks:\n"""
        for owner in individual_task:
            i_tab = tabulate(individual_task[owner], headers='keys', tablefmt='grid')
            message = message + f'task owner: {owner}\n```\n' + i_tab + '\n```\n'

        self.api.messages.create(markdown=message,
                                 roomId=self.data['roomId'])

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
        task_data = re.sub('^reportees remove task\s', '', message)
        if not task_data:
            self.send_message(
                "Invalid input. Specify a task id to delete")
            return
        task_object = TodoManager(self.user)
        result = task_object.delete_task(task_data)
        if result == None:
            self.send_message(f"No task exists with task id: {task_data}")
            return
        if result == False:
            self.send_message(f"Failed to delete task: {task_data}")
        else:
            self.send_message(f"Removed task: {task_data}")

    def modify_task_from_reportees(self, data, message):
        task_data = re.sub('^reportees modify task\s', '', message)

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

        required = ['task_id']
        valid_task = all([x in task_data for x in required])
        if not valid_task:
            self.send_message(
                f"Valid parameters not passed to the command. following parameters are required: {', '.join(required)}")
            return

        try:
            duedate = datetime.datetime.strptime(task_data['due'], "%d/%m/%y %H:%M:%S") if task_data.get(
                'due') else None
        except ValueError:
            self.send_message(
                "Invalid date format for due date. Please specify the due date in following format: dd/mm/yy HH:MM:SS")
            return

        if duedate:
            task_data['due'] = duedate
        task_id = task_data['task_id']
        del task_data['task_id']
        tasks_object = TodoManager(self.user)
        valid_params = all([x in tasks_object.permitted_fields for x in task_data])
        if not valid_params:
            self.send_message(
                f"Valid parameters were not passed to the command. "
                f"Permitted keys are: {', '.join(tasks_object.permitted_fields)}")
            return

        status = tasks_object.reportees_modify_task(task_id, task_data)
        if status == None:
            self.send_message(f"Sorry, the task id {task_id} does not exist in the reportees task list.")
        elif status == False:
            self.send_message(f"Error in modifying the task. Please try again")
        else:
            self.send_message(f"Task {task_id} modified successfully")

    def list_group_tasks_from_reportees(self, data, message):
        tasks_object = TodoManager(self.user)
        reportees_task, individual_task = tasks_object.get_reportees_tasks()
        message = ""
        if reportees_task:
            message = """### Group tasks:\n"""
            group_tab = tabulate(reportees_task.values(), headers='keys', tablefmt="grid")
            message = message + '```\n' + group_tab + '\n```\n'
        else:
            message = """### No Group tasks exist\n"""

        self.api.messages.create(markdown=message,
                                 roomId=self.data['roomId'])

    def send_message(self, text):
        self.api.messages.create(text=text, roomId=self.data['roomId'])