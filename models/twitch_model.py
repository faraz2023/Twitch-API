from models.db_model import DbHandler
from models.chatlog import ChatLog
from models.channel import Channel
import sqlite3
import settings
import json

class Twitch():

    # SINGLETON PATTERN
    __instance = None
    def __init__(self):
        if Twitch.__instance == None:
            # create handler for connection to database

            try:
                self.db_handler = DbHandler(settings.DATABASE_NAME)
            except TypeError as e:#pragma: no cover
                # Already instantiated
                self.db_handler = DbHandler.getInstance()

            self.chatlogs = {}
            self.logger = settings.twitch_logger
            Twitch.__instance = self
        else:
            raise TypeError("Twitch model cannot have multiple instances")


    @staticmethod
    def getInstance():
        return Twitch.__instance


    # creates a channel based on channel_id and channel_name
    def create_channel(self, channel_id, channel_name):
        channel = Channel(channel_id, channel_name)
        try:
            channel.save(self.db_handler)
        except sqlite3.DatabaseError as e:
            # Channel exists
            pass
        return channel

    # parses a chatlog and returns a dictionary composed of chatlog file. Requires a json file path
    def parse_chatlog(self, filename):
        try:
            chatlog = ChatLog(filename)
            #add the chatlog instace into the chatlogs dictionary
            self.chatlogs[filename] = chatlog
            return chatlog.get_chatlog()
        except FileNotFoundError as e:
            self.logger.error('Twitch failed to parse chatlog ({}). File not found.'.format(filename))
            raise FileNotFoundError("Failed to parse {}. File not found.".format(filename))


    # Returns a list where each element is a dictionary with key comment body
    # and key value a tuple where the first element is the number of the comment's repetitions
    # in the chat log and the second element is the list of users who have posted this comment.
    # If `sort` is True, the elements will be sorted in the returned list.
    def process_comments(self, chatlog_name, sort=False):
        # check if the chatlog is already parsed
        if not chatlog_name in self.chatlogs.keys():
            self.logger.error('({}) is not an imported chatlog.'.format(chatlog_name))
            raise KeyError("({}) is not in chatlogs".format(chatlog_name))

        # retrives the chatlog
        chatlog = self.chatlogs[chatlog_name]

        # counts the number of occurrences for each comment
        comments = chatlog.count_comments()
        self.logger.info('({}) successfully processed based on comment repetition.'.format(chatlog_name))
        # sorts the return list if sort is true
        if (sort):
            return sorted(comments.items(), key=lambda kv:kv[1][0], reverse=True)
        return comments.items()




    # Deletes spam with channel_id and stream_id provided
    def delete_top_spam(self, channel_id, stream_id):
        self.db_handler.delete_from_database('top_spam', ['channel_id eq ' + channel_id,\
            'stream_id eq ' + stream_id], 'AND')


    # Recives a list of comments and a threshold to return all the comments that have been repeated
    # more than the threshold
    def insert_top_spam(self, comments, threshold = settings.TOP_SPAM_THRESHOLD):
        try:
            spam_count = 0
            for index,(comment_body,comment_data) in enumerate(comments):
                # check number of comment occurences
                if comment_data[0] > threshold:
                    # values is [channel_id, stream_id, comment, comment_count, user_count]
                    values = [comment_data[2], comment_data[3], comment_body, comment_data[0], len(comment_data[1])]
                    self.db_handler.insert_values('top_spam', values)
                    self.logger.info("Channel id: ({}) Inserted comment.".format(comment_data[2]))
                    spam_count += 1

            self.logger.info('Successfully inserted {} comments into database'.format(spam_count))

            return spam_count

        except (sqlite3.DatabaseError, TypeError) as e:
            self.logger.error('Failed to insert comments into database')
            raise e("failed to insert comments into database")

    # Returns from the databse all the comments that have channel_id and stream_id
    def get_top_spam(self, channel_id, stream_id):

        conditions = ['channel_id eq ' + channel_id, 'stream_id eq ' + stream_id]

        # Select 'spam_text', 'occurrences', 'user_count'
        top_spam = self.db_handler.select_from_database('top_spam', ['spam_text', \
            'spam_occurrences', 'spam_user_count'], conditions, 'AND', \
            'spam_occurrences desc, spam_user_count desc, spam_text', '')

        # Rename column names in dictionary
        for spam in top_spam:
            spam["occurrences"] = spam.pop("spam_occurrences")
            spam["user_count"] = spam.pop("spam_user_count")

        return top_spam


    def get_top_spam2(self, channel_id, stream_id, threshold = settings.TOP_SPAM_THRESHOLD):# pragma: no cover

        conditions = ['channel_id eq ' + channel_id, 'stream_id eq ' + stream_id]

        # Select 'spam_text', 'occurrences', 'user_count'
        top_spam = self.db_handler.select_from_database('chat_log', ['text as spam_text', \
            'COUNT(*) as occurrences', 'COUNT(DISTINCT user) as user_count'], conditions, 'AND', \
            'occurrences desc, user_count desc, spam_text', '', \
            'text HAVING occurrences > ' + str(threshold))

        return top_spam

    def delete_chatlog(self, channel_id, stream_id):# pragma: no cover
        self.db_handler.delete_from_database('chat_log', ['channel_id eq ' + channel_id,\
            'stream_id eq ' + stream_id], 'AND')


    # Inserts an already parsed chatlog file into the database, chat_logs table
    def insert_chatlog(self, filename):
        # Check if chat log has been imported & parsed
        if not filename in self.chatlogs.keys():
            self.logger.error('({}) is not an imported chatlog.'.format(filename))
            raise KeyError("File is not in chatlogs")

        # Retrieves this files data from the chatlogs dictionary
        chatlog = self.chatlogs[filename].get_chatlog()

        channel_id = ''
        stream_id = ''
        insert_values = []
        # Get the values from comments needed to insert into chatlog
        for comment in chatlog['comments']:
            channel_id = comment['channel_id']
            stream_id = comment['content_id']
            comment_body = comment['message']['body']
            commenter_display_name = comment['commenter']['display_name']
            created_at = comment['created_at']
            content_offset_seconds = comment['content_offset_seconds']
            # Append list to list of values
            insert_values.append([channel_id, stream_id, comment_body, commenter_display_name,\
                      created_at, content_offset_seconds])

        try:
            # insert into the data base the comments that have been processed
            insert_failure_count = self.db_handler.insert_multiple_values('chat_log', insert_values)
            return [len(insert_values), insert_failure_count, stream_id, channel_id]
        except sqlite3.DatabaseError as e:# pragma: no cover
            self.logger.error("could not insert values with channel id {} to database".format(channel_id))
            raise e("could not insert values")

    def query_chatlog(self, filters):
        string_columns = ['text', 'user']

        # Make sure filter is in correct format for string columns
        for index, filter in enumerate(filters):

            if not isinstance(filter, str) or len(filter.split(' ')) != 3:
                raise TypeError("All filters are not in the correct format")

            [column, operator, value] = filter.split(' ')
            if column in string_columns:
                value = "'" + value + "'"
            filters[index] = " ".join([column, operator, value])

        return self.db_handler.select_from_database('chat_log', ['*'], filters, 'AND', 'chat_time', '')


    # Get per minutes metrics of comments made by users in a given channel and
    # stream
    def get_viewer_metrics(self, channel_id, stream_id):# pragma: no cover
        conditions = ['channel_id eq ' + channel_id, 'stream_id eq ' + stream_id]

        # Get metrics from database
        metrics = self.db_handler.select_from_database('chat_log', ['channel_id', \
            'stream_id', 'chat_time', 'COUNT(*) as messages',\
            'COUNT(DISTINCT user) as viewers'], conditions, 'AND', \
            'chat_time', 'ASC', \
            "strftime('%Y-%m-%dT%H:%M:%S.000', chat_time)")

        # Return empty list if database is empty
        if not len(metrics):
            return metrics

        # Create viewer ship dictionary to be returned
        viewership_metrics = {"channel_id": channel_id, "stream_id": stream_id,
            "starttime": metrics[0]['chat_time'], "per_minute": []}

        # Create first per minute dictionary with no data
        current_offset = 1
        metric = {"offset": current_offset, "viewers": 0, "messages": 0}
        viewership_metrics['per_minute'].append(metric)

        # Iterate through per second metrics and add to per minute dictionary
        for index, seconds_metric in enumerate(metrics):
            # Check if index is at new offset and create new per minute dictionary
            if current_offset != ((index // 60) + 1):
                current_offset = ((index // 60) + 1)
                viewership_metrics['per_minute'].append(\
                {"offset": current_offset, "viewers": 0, "messages": 0})

            # Get last metric
            current_metric = viewership_metrics['per_minute'][-1]

            # current_metric['viewers'] += seconds_metric['viewers']
            current_metric['messages'] += seconds_metric['messages']


        return [viewership_metrics]
