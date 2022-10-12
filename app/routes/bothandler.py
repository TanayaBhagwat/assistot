from app.routes import handlerbp
import flask
import traceback
from webexteamssdk import WebexTeamsAPI
from app.bot import Bot
from app.routes.config import QUEUE_BOT, PRODUCTION
import pprint
import logging
import datetime

from app.routes.config import LOGGER_CONFIG
logger = logging.getLogger(LOGGER_CONFIG['NAME'])
FORMAT_STRING = '%I:%M:%S %p on %a, %b %d'
TIMEOUT = 5000
CSV_FILE_FORMAT = '{}-{}-STATISTICS.csv'
VERSION = '1.0.0'
RELEASED = str(datetime.datetime(year=2022, month=10, day=1))
AUTHOR = 'Sumit Chachadi'
EMAIL = 'sumitmcc@gmail.com'

# userbp blueprint created in  routes/__init__.py and registered to app in application factory
@handlerbp.route('/handler', methods=['POST'])
def handle_bot():
    data = flask.request.json
    try:
        if data:

            logger.debug('Initializing SVS todobot')
            if PRODUCTION:
                api = WebexTeamsAPI(QUEUE_BOT)
            else:
                from app.routes.config import DEV_QUEUE_BOT
                api = WebexTeamsAPI(DEV_QUEUE_BOT)

            logger.debug('Webex API initialized')

            data = data['data']
            logger.debug(data)
            me_id = api.people.me().id

            if data.get('personId') != me_id and data.get('roomType') == 'direct':
                logger.debug(pprint.pformat(data))
                BOT = Bot(api, data)
                if not BOT.valid_user:
                    api.messages.create(roomId=data['roomId'],parentId=data['id'], text='You are not permitted to use this bot, please contact schachad@cisco.com')
                    return ''
                BOT.data_handler(data)

            return ''

        else:
            return 'NO STOP PLEASE STOP'
    except Exception as e:
        if not PRODUCTION:
            raise
        print(traceback.format_exc())
        logger.error(traceback.format_exc())
        return '500 Internal Server Error'

