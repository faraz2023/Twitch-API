import unittest
import sqlite3
import json
from models.twitch_model import Twitch
from models.chatlog import ChatLog

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
        filename = 'tests/test_files/test_corrupt_comment.json'
        chatlog = ChatLog(filename)

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


if __name__ == '__main__':
    unittest.main()
