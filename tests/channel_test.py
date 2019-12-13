import unittest
import sqlite3
from models.channel import Channel
from models.twitch_model import Twitch

class TestChannel(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.twitch = Twitch()


    def test_create_channel(self):

        with self.assertRaises(TypeError):
            channel = Channel(1234)

    def test_save_channel(self):

       channel1 = Channel(1234, 'test_channel')
       channel1.save(self.twitch.db_handler)

       with self.assertRaises(sqlite3.DatabaseError):
           channel2 = Channel(1234, 'test_channel2')
           channel2.save(self.twitch.db_handler)

    def test_channel_str(self):
        channel1 = Channel(1234, 'test_channel')
        self.assertEqual([channel1.channel_id, channel1.channel_name],[1234, 'test_channel'])

    def test_channel_to_string(self):
        channel1 = Channel(1234, 'test_channel')
        self.assertEqual(channel1.__str__(), "(1234, 'test_channel')")


if __name__ == '__main__':
    unittest.main()
