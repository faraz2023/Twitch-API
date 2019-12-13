import unittest
import sqlite3
import json
from models.twitch_model import Twitch
from models.chatlog import ChatLog
from models.db_model import DbHandler

class TestTwitch(unittest.TestCase):


    @classmethod
    def setUpClass(self):
        self.twitch = Twitch()

    # to test the Singleton pattern
    def test_singleton(self):
        with self.assertRaises(TypeError):
            failedTwitch = Twitch()

    # to test get instance
    def test_get_instance(self):
        self.assertEqual(self.twitch, Twitch.getInstance())


    def test_create_channel(self):
        # creating a channel
        channel = self.twitch.create_channel(12345, 'test_channel')
        self.assertEqual(channel.channel_id, 12345)
        self.assertEqual(channel.channel_name, 'test_channel')
        self.assertEqual(channel.__str__(), "(12345, 'test_channel')")

        #type error if wrong parameters are sent
        with self.assertRaises(TypeError):
            self.twitch.create_channel(123456)
        with self.assertRaises(TypeError):
            self.twitch.create_channel('fake_channel')

        # if a channel already exists the app just passes
        self.twitch.create_channel(12345, 'test_channel')

    def test_parse_chatlog(self):
        filename = 'shdvsnyxl.json'
        crap_filename = 'notjson.notjson'
        not_json_file = 'tests/test_files/not_valid_json.json'

        with self.assertRaises(FileNotFoundError):
            self.twitch.parse_chatlog(crap_filename)

        with self.assertRaises(json.JSONDecodeError):
            self.twitch.parse_chatlog(not_json_file)

        chatlog = ChatLog(filename).get_chatlog()
        chatlog2 = self.twitch.parse_chatlog(filename)

        self.assertEqual(chatlog, chatlog2)

    def test_count_comments(self):
        chatlog = ChatLog('tests/test_files/test_comment.json')
        outcome = {'PLEASE BE A FAIR MATCH, to get more hours of tokens': (1, {'seaskythe'}, '137512364', '451603129')}
        self.assertEqual(chatlog.count_comments(), outcome)

        chatlog = ChatLog('tests/test_files/test_corrupt_comment.json')
        with self.assertRaises(KeyError):
            chatlog.count_comments()

    def test_proccess_comments(self):
        filename = 'tests/test_files/test_comment.json'
        chatlog = self.twitch.parse_chatlog(filename)

        # test where chatlog is not already parsed
        with self.assertRaises(KeyError):
            self.twitch.process_comments('fakename')

        test_result = [('PLEASE BE A FAIR MATCH, to get more hours of tokens', (1, {'seaskythe'}, '137512364', '451603129'))]

        # check without sort
        self.assertEqual(list(self.twitch.process_comments(filename)), test_result)

        # check with sort
        self.assertEqual(list(self.twitch.process_comments(filename, sort=True)), test_result)


    def test_insert_top_spam(self):

        # asserts type error if input is corrupted
        with self.assertRaises(TypeError):
            self.twitch.insert_top_spam([12334,2323,'322'])

        # assert that count comments counts properly when given correct format
        filename = 'tests/test_files/test_comment.json'
        chatlog = self.twitch.parse_chatlog(filename)
        comments = self.twitch.process_comments(filename)
        self.assertEqual(self.twitch.insert_top_spam(comments, 0), 1)



    def test_get_top_spam(self):

        # assert type error
        with self.assertRaises(TypeError):
            self.twitch.create_channel('1223344')

        # assert that get top spam works properly when given correct format
        self.twitch.delete_top_spam('137512364', '451603129')
        filename = 'tests/test_files/test_comment.json'
        chatlog = self.twitch.parse_chatlog(filename)
        comments = self.twitch.process_comments(filename)
        self.twitch.insert_top_spam(comments, 0)
        test_outcome = [{'spam_text': 'PLEASE BE A FAIR MATCH, to get more hours of tokens', 'occurrences': 1, 'user_count': 1}]
        self.assertEqual(self.twitch.get_top_spam('137512364', '451603129'), test_outcome)



    def test_delete_chatlog(self):

        with self.assertRaises(TypeError):
            self.twitch.delete_chatlog('1223344')

    def test_insert_chatlog(self):
        filename = 'shdvsnyxl.json'
        chatlog = self.twitch.parse_chatlog(filename)

        with self.assertRaises(KeyError):
            self.twitch.insert_chatlog('fakename')

        self.assertEqual(self.twitch.insert_chatlog(filename), [23894, 0, '451603129', '137512364'])


    def test_query_chatlog(self):

        with self.assertRaises(TypeError):
            self.twitch.query_chatlog(1234)

        with self.assertRaises(TypeError):
            self.twitch.query_chatlog('qwe 123')

        result = [{'channel_id': 137512364, 'stream_id': 451603129,\
        'text': 'reward A Cheer shared Rewards to 10 others in Chat!',\
        'user': 'InfiniteSoulOW', 'chat_time': '2019-07-12T04:17:23.973304871Z',\
        'offset': 1}]

        self.assertEqual(self.twitch.query_chatlog(['user eq InfiniteSoulOW']), result)

    # --- Database Handler ---

    def test_instantiation(self):
        # Raises TypeError if parameters are not right
        with self.assertRaises(TypeError):
            db_handler = DbHandler(None)

        self.assertEqual(self.twitch.db_handler.database_name, 'twitch.db')

    def test_get_db_instance(self):
        self.assertEqual(self.twitch.db_handler, DbHandler.getInstance())


    def test_open_connection(self):
        self.twitch.db_handler.database_name = None

        with self.assertRaises(sqlite3.DatabaseError):
            self.twitch.db_handler.set_up_twitch_db()

        self.twitch.db_handler.database_name = 'twitch.db'


    def test_insert(self):

        # Raises Database error if we try to insert in non existent table
        with self.assertRaises(sqlite3.DatabaseError):
            self.twitch.db_handler.insert_values("fake_table", [12, 13])

        # Raises Database error if values are passed in a wrong manner
        with self.assertRaises(sqlite3.DatabaseError):
            self.twitch.db_handler.insert_values("chat_logs", [12, 13])

        # inserts the values into the database succesfully
        self.twitch.db_handler.insert_values("channels", [12346, 'test_channel'])

        # checks if the values are inserted correctly
        test_outcome =self.twitch.db_handler.select_from_database('channels', ['*'], ['channel_id eq 12346'])
        self.assertEqual(test_outcome[0]['channel_id'], 12346)
        self.assertEqual(test_outcome[0]['channel_name'], 'test_channel')


    def test_multiple_insert(self):

        # channels to be inserted
        channels = [[1, 'test'], [2, 'test'], [3, 'test'], [4, 'test'],[5, 1, 'test']]

        # inserting the channels
        not_inserted = self.twitch.db_handler.insert_multiple_values('channels', channels)

        # the desirable outcome
        test_outcome = [{'channel_id': 1, 'channel_name': 'test'},  {'channel_id': 2, 'channel_name': 'test'},\
                        {'channel_id': 3, 'channel_name': 'test'}, {'channel_id': 4, 'channel_name': 'test'}]

        # calling to get the outcome
        out = self.twitch.db_handler.select_from_database('channels', ['*'], ['channel_id lt 6'])

        #asseriting equal
        self.assertEqual(test_outcome, out)
        self.assertEqual(not_inserted, 1)

    def test_select_from_databse(self):

        test_outcome = [{'channel_id': 1, 'channel_name': 'test'},\
            {'channel_id': 2, 'channel_name': 'test'},\
            {'channel_id': 3, 'channel_name': 'test'},\
            {'channel_id': 4, 'channel_name': 'test'},\
            {'channel_id': 12345, 'channel_name': 'test_channel'},\
            {'channel_id': 12346, 'channel_name': 'test_channel'}]

        # Test with all invalid condition
        self.assertEqual(self.twitch.db_handler.select_from_database('channels', ['*'], ['channel_id 123456', '12345'])\
                         , test_outcome)


        # inserts the values into the database succesfully
        self.twitch.db_handler.insert_values("channels", [123457, 'test_channel'])
        self.twitch.db_handler.insert_values("channels", [123458, 'test_channel1'])
        self.twitch.db_handler.insert_values("channels", [123459, 'test_channel2'])

        test_outcome = [{'channel_id': 123457, "channel_name": 'test_channel'},\
                         {'channel_id': 123458, "channel_name": 'test_channel1'},\
                         {'channel_id': 123459, "channel_name": 'test_channel2'}]

        self.assertEqual(self.twitch.db_handler.select_from_database('channels', ['*'], ['channel_id gt 123456'])\
                         , test_outcome)

        # Test with invalid and_or
        self.assertEqual(self.twitch.db_handler.select_from_database('channels', ['*'], ['channel_id gt 123456'],\
            and_or="NOTHING"), test_outcome)


        with self.assertRaises(sqlite3.DatabaseError):
            self.twitch.db_handler.select_from_database('channels', ['channel_id', '*'])

        # Test with 1 invalid condition
        self.assertEqual(self.twitch.db_handler.select_from_database('channels', ['*'], ['channel_id gt 123456', '12345'])\
                         , test_outcome)

        # Test group by
        test_outcome = [{'channel_id': 1, 'channel_name': 'test'},\
        {'channel_id': 12345, 'channel_name': 'test_channel'},\
        {'channel_id': 123458, 'channel_name': 'test_channel1'},\
        {'channel_id': 123459, 'channel_name': 'test_channel2'}]

        self.assertEqual(self.twitch.db_handler.select_from_database('channels', ['*'], group_by='channel_name')\
                         , test_outcome)

        with self.assertRaises(sqlite3.DatabaseError):
            self.twitch.db_handler.select_from_database('channels', ['DOES_NOT_EXIST'])


    def test_condition_to_sql_str(self):

        result = []
        self.assertEqual(self.twitch.db_handler.select_from_database('channels', ['*'],\
        ['channel_id gteq 123459', 'channel_id eq 123459', 'channel_id lt 1',\
        'channel_id lteq 1',"channel_name like 'test_channel2'"], and_or="OR"), result)


    def test_delete_from_database(self):

        # inserting some random channels
        channel = [6, 'test']
        self.twitch.db_handler.insert_values("channels", channel)

        #assert the channel exists
        test_outcome = [{'channel_id': 6, "channel_name": 'test'}]
        self.assertEqual(self.twitch.db_handler.select_from_database('channels', ['*'], ['channel_id eq 6']) \
                         , test_outcome)

        # asserting failure with delete without conditions
        with self.assertRaises(sqlite3.DatabaseError):
            self.twitch.db_handler.delete_from_database('channels')

        with self.assertRaises(sqlite3.DatabaseError):
            self.twitch.db_handler.delete_from_database('channels', conditions=['1234'])

        # deleting the channel with invalid condition
        invalid = self.twitch.db_handler.delete_from_database('channels', conditions=['channel_id eq 6', '1234'])

        self.assertEqual(invalid, 1)

        self.twitch.db_handler.delete_from_database('channels', conditions=['channel_id eq 6'])

        #asserting the channel does not exist anymore
        test_outcome = []
        self.assertEqual(self.twitch.db_handler.select_from_database('channels', ['*'], ['channel_id eq 6']) \
                         , test_outcome)



if __name__ == '__main__':
    unittest.main()
