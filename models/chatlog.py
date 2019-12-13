import json
import settings

class ChatLog():

    def __init__(self, filename):
        self.filename = filename
        self.chat_log = None
        self.logger = settings.chatlog_logger
        try:
            with open(self.filename) as file:
                self.chat_log = json.load(file)
                self.logger.info('Chatlog instance was created and ({}) was successfully imported.'.format(self.filename))
        except FileNotFoundError as e:
            self.logger.error('Chatlog constructor failed to open ({}). Needed json.'.format(self.filename))
            raise e

    def get_chatlog(self):
        return self.chat_log

    # count the occurences of comments and track users that made each comment
    # returns dictionary {comment<str>: tupple(count<int>, users<set>)}
    def count_comments(self):

        try:
            count_comments_and_users = {}

            # iterate through comments and count occurences
            for comment in self.chat_log['comments']:
                user = comment["commenter"]["display_name"]
                message_body = comment["message"]["body"]
                channel_id = comment["channel_id"]
                stream_id = comment["content_id"]
                (count, users, channel_id, stream_id) = count_comments_and_users.get(message_body, (0, set(), channel_id, stream_id))
                count += 1
                users.add(user)
                count_comments_and_users[message_body] = (count, users, channel_id, stream_id)

            self.logger.info('Comments at ({})successfully counted based on repetition.'.format(self.filename))
            return count_comments_and_users
        except KeyError as e:
            self.logger.error('Could not count comments at ({}).'.format(self.filename))
            raise e
