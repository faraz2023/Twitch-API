import logging
import os


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='./logs/std_logs.log',
                    filemode='a')

db_logger = logging.getLogger('db_model')
chatlog_logger = logging.getLogger('chatlog_model')
twitch_logger = logging.getLogger('twitch_model')
channel_logger = logging.getLogger('channel_logger')

TOP_SPAM_THRESHOLD = 10

# Build database paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASE_NAME = 'twitch.db'
