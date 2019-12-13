import sqlite3
import settings
class Channel():

    def __init__(self, channel_id, channel_name):
        self.channel_id = channel_id
        self.channel_name = channel_name
        self.table_name = 'channels'
        self.logger = settings.channel_logger

    def save(self, db_handler):
        try:
            db_handler.insert_values(self.table_name, [self.channel_id, self.channel_name])
            self.logger.info("added new instance of channel with id: {} and name {}"\
                             .format(self.channel_id, self.channel_name))
        except sqlite3.DatabaseError as e:
            self.logger.error("failed to add new instance of channel with id: {} and name {}" \
                             .format(self.channel_id, self.channel_name))
            raise sqlite3.DatabaseError(e)

    def __str__(self):
        return str(tuple([self.channel_id, self.channel_name]))
