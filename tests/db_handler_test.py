import unittest
import sqlite3
from models.db_model import DbHandler

class MyTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.db_handler = DbHandler('twitch.db')
        self.db_handler.set_up_twitch_db()


    def test_instanciation(self):
        # Raises TypeError if parameters are not right
        with self.assertRaises(TypeError):
            db_handler = DbHandler()

        self.assertEqual(self.db_handler.database_name, 'twitch.db')

    def test_insert(self):

        # Raises Database error if we try to insert in non existent table
        with self.assertRaises(sqlite3.DatabaseError):
            self.db_handler.insert_values("fake_table", [12, 13])

        # Raises Database error if values are passed in a wrong manner
        with self.assertRaises(sqlite3.DatabaseError):
            self.db_handler.insert_values("chat_logs", [12, 13])

        # inserts the values into the database succesfully
        self.db_handler.insert_values("channels", [12346, 'test_channel'])

        # checks if the values are inserted correctly
        test_outcome =self.db_handler.select_from_database('channels', ['*'], ['channel_id eq 12346'])
        self.assertEqual(test_outcome[0]['channel_id'], 12346)
        self.assertEqual(test_outcome[0]['channel_name'], 'test_channel')

    def test_multiple_insert(self):

        # channels to be inserted
        channels = [[1, 'test'], [2, 'test'], [3, 'test'], [4, 'test']]

        # inserting the channels
        self.db_handler.insert_multiple_values('channels', channels)

        # the desirable outcome
        test_outcome = [{'channel_id': 1, 'channel_name': 'test'},  {'channel_id': 2, 'channel_name': 'test'},\
                        {'channel_id': 3, 'channel_name': 'test'}, {'channel_id': 4, 'channel_name': 'test'}]

        # calling to get the outcome
        out = self.db_handler.select_from_database('channels', ['*'], ['channel_id lt 6'])

        #asseriting equal
        self.assertEqual(test_outcome, out)

    def select_from_databse(self):

        # inserts the values into the database succesfully
        self.db_handler.insert_values("channels", [12345, 'test_channel'])
        self.db_handler.insert_values("channels", [12344, 'test_channel1'])
        self.db_handler.insert_values("channels", [12343, 'test_channel2'])

        test_outcome = [{'channel_id': 12345, "channel_name": 'test_channel'},\
                         {'channel_id': 12344, "channel_name": 'test_channel1'},\
                         {'channel_id': 12343, "channel_name": 'test_channel2'}]

        self.assertEqual(self.db_handler.select_from_database('channels', ['*'], ['channel_id lt 12345'])\
                         , test_outcome)



    def test_delete_from_database(self):


        # inserting some random channels
        channel = [6, 'test']
        self.db_handler.insert_values("channels", channel)

        #assert the channel exists
        test_outcome = [{'channel_id': 6, "channel_name": 'test'}]
        self.assertEqual(self.db_handler.select_from_database('channels', ['*'], ['channel_id eq 6']) \
                         , test_outcome)

        # asserting failure with delete without conditions
        with self.assertRaises(sqlite3.DatabaseError):
            self.db_handler.delete_from_database('channels')

        # deleting the channel
        self.db_handler.delete_from_database('channels', conditions=['channel_id eq 6'])

        #asserting the channel does not exist anymore
        test_outcome = []
        self.assertEqual(self.db_handler.select_from_database('channels', ['*'], ['channel_id eq 6']) \
                         , test_outcome)


if __name__ == '__main__':
    unittest.main()
