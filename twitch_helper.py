import argparse

def create_argument_parser():
    # creating parsing  functionality for the application
    argument_parser = argparse.ArgumentParser(description='Parsing the command line arguments for twitch application')

    # sub-commands functionality
    sub_parser = argument_parser.add_subparsers(dest='sub')

    # look for create channel functionality and add arguments to parser
    parser_create_channel = sub_parser.add_parser('createchannel')
    parser_create_channel.add_argument('channel_name')
    parser_create_channel.add_argument('channel_id', type=int)

    # look for parst top spam functionality and add arguments to parser
    parser_pars_topspam = sub_parser.add_parser('parsetopspam')
    parser_pars_topspam.add_argument('file')

    # look for get top spam command and add arguments to parser
    parser_get_topspam = sub_parser.add_parser('gettopspam')
    parser_get_topspam.add_argument("channel_id")
    parser_get_topspam.add_argument("stream_id")

    # look for get top spam enhancement command and add arguments to parser
    parser_get_topspam = sub_parser.add_parser('gettopspam2')
    parser_get_topspam.add_argument("channel_id")
    parser_get_topspam.add_argument("stream_id")

    # look for storing chat log functionality and add file name argument to parser
    parser_store_chatlog = sub_parser.add_parser("storechatlog")
    parser_store_chatlog.add_argument('file')

    # look for querying the chat log with filers
    parser_query_chatlog = sub_parser.add_parser("querychatlog")
    parser_query_chatlog.add_argument("filters",nargs="+")

    # look for get viewership metrics command and add arguments to parser
    parser_get_topspam = sub_parser.add_parser('viewership')
    parser_get_topspam.add_argument("channel_id")
    parser_get_topspam.add_argument("stream_id")

    return argument_parser
