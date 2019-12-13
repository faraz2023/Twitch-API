import json
import sys
import sqlite3
from twitch_helper import create_argument_parser
from models.twitch_model import Twitch


def main():

    # parse arguments provided
    argument_parser = create_argument_parser()
    parser = argument_parser.parse_args()

    try:
        twitch = Twitch()
    except TypeError as e:
        # Already instantiated
        twitch = Twitch.getInstance()

    if parser.sub == "createchannel":
        channel = twitch.create_channel(parser.channel_id, parser.channel_name)
        print(channel)
    elif parser.sub == "parsetopspam":

        twitch.parse_chatlog(parser.file)
        comments = twitch.process_comments(parser.file, True)
        stream_id = comments[0][1][3]
        channel_id = comments[0][1][2]
        twitch.delete_top_spam(channel_id, stream_id)
        spam_count = twitch.insert_top_spam(comments)

        print("inserted {} top spam records for stream {} on channel {}".format(spam_count, stream_id, channel_id))

    elif parser.sub == "gettopspam":
        print(json.dumps(twitch.get_top_spam(parser.channel_id, parser.stream_id)))

    elif parser.sub == "gettopspam2":
        print(json.dumps(twitch.get_top_spam2(parser.channel_id, parser.stream_id)))

    elif parser.sub == "storechatlog":

        chatlog = twitch.parse_chatlog(parser.file)
        channel_id = chatlog['comments'][0]['channel_id']
        stream_id = chatlog['comments'][0]['content_id']
        twitch.delete_chatlog(channel_id, stream_id)
        inserted_chatlog_stat = twitch.insert_chatlog(parser.file)

        print("inserted {} records to chat log for stream {} on channel {}"\
        .format(inserted_chatlog_stat[0]-inserted_chatlog_stat[1], inserted_chatlog_stat[2], inserted_chatlog_stat[3]))

    elif parser.sub == 'querychatlog':
        result = twitch.query_chatlog(parser.filters)
        print(json.dumps(result))

    elif parser.sub == 'viewership':
        print(json.dumps(twitch.get_viewer_metrics(parser.channel_id, parser.stream_id)))



if __name__== "__main__":
    main()
