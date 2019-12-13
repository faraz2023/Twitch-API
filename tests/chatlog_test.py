import unittest
import sqlite3
from models.channel import Channel
from models.twitch_model import Twitch
from models.chatlog import ChatLog

class TestChatlog(unittest.TestCase):


    def test_instanciation(self):

        with self.assertRaises(TypeError):
            chatlog = ChatLog()

        with self.assertRaises(FileNotFoundError):
            chatlog = ChatLog('notjson.json')

    def test_count_comments(self):

        chatlog = ChatLog('tests/test_files/test_comment.json')
        outcome = {'PLEASE BE A FAIR MATCH, to get more hours of tokens': (1, {'seaskythe'}, '137512364', '451603129')}
        self.assertEqual(chatlog.count_comments(), outcome)

        chatlog = ChatLog('tests/test_files/test_corrupt_comment.json')
        with self.assertRaises(KeyError):
            chatlog.count_comments()

if __name__ == '__main__':
    unittest.main()
