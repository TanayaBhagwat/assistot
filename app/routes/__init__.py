from flask import Blueprint
import logging
import datetime

todobp = Blueprint('todo', __name__)
userbp = Blueprint('user', __name__)
handlerbp = Blueprint('handler', __name__)

from app.routes import user
from app.routes import todo
from app.routes import bothandler
