# Twitch API

#### Class Design:

- `DbHandler` is responsible purely and only for database access and functionality
  including opening connections, executing queries, committing queries, and closing connections. + List of public methods:
  _ `insert_values(tablename<str>, values<list>)`: Gets a list of values and adds them as a row to the table with
  `tablename`. If the table does not exist or if the size of values list is not equal to the number of columns in the table, exceptions will be thrown.
  _ `insert_multiple_values(table_name<str>, values<list>)`: Gets a list of list as values and adds each list as a row to the table with name `tablename`. Table must exist and each list in `values`
  must have the same size as the number of columns in `tablename` \* `select_from_database(table_name<str>, columns<list>, conditions<list>, and_or=<str>, order_by=<str>, ASC_DESC=<str>)`: selects from `table_name` the rows that meet `condiitons`. See code documentations
  for more info.

- `Twitch` handles a whole instance of our twitch application. Twitch follows SINGLETON patter. It keeps track of `chatlogs` and `channels`.
  In addition, `twitch_model` facilitates conversation between database handler and other classes in order to make queries such as `insert_top_spam` + List of public methods:
  _ `create_channel(channel_id<int>, channel_name<str>)`: Creates a new instance of Channel class and adds the channel to the database. <br>
  _ `parse_chatlog(filename<str>)`: Creates an instance of `Chatlog` class, adds it to the `twitch_model`'s chatlog dictionary and returns the newly created chatlog. <br>
  _ `process_comments(chatlog_name<str>, sort<bool>)`: Gets the name of a chatlog file, if the file is already parsed, return a list where each element is a dictionary with key comment body
  and key value a tuple where the first element is the number of the comment's repetitions in the chat log and the second element is the list of users who have posted this comment.
  If `sort` is True, the elements will be sorted in the returned list.
  _ `insert_top_spam(comments<list>, threshold<int>, sort<bool>`: Receives a list in the format of `proccess_comments` return value and inserts into the database all the comments
  that have been repeated more than the `threshold`
  _`get_top_spam(channel_id<str>, stream_id<str>)`: Selects (thorough `db_model`) all the rows of the `top_spam` table where the channel_id and stream_id conforms and returns a list of the selected rows.
  _`clean_old_chatlog(channel_id<str>, stream_id<str>)`: Deletes (thorough `db_model`) all the rows of the `chat_log` table where the channel_id and stream_id conforms \*`insert_chatlog(filename<str>)`: Inserts (thorough `db_model`) a chatlog file into `chat_log` table

- `ChatLog` handles single instances of chatlogs. It is used by `Twitch` to get the top spams.

  - List of public methods:
    - `get_chatlog()`: Returns this instance's chatlog dictionary
    - `count_comments()`: Returns a dictionary where each key is a unique message body in this instance chatlog and each key value is
      a tuple of the number of occurrences of this comments and name of users who have posted the comment

- `Channel` handles single instaces of channels. This class allows the `Twitch` class to save channels into the database
  - List of public methods:
    - `save(db_handler<DbHandler)`: Saves this channel into the `db_handler`. <br>
    - `__str__()` has been implemented to address needs of the twitch.py. <br>

### Loggers:

We have implemented a logger using python native library `logging`. Each class has its own logger, listed below:
_`DbHandler`: db_model
_ `Twitch`: chatlog_model
_ `ChatLog`: twitch_model
_ `Channel`: channel_loger

Every event above DEBUG level is logged in format:<br>
`format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s` <br>
The log file can be found at <br>
`logs\std_logs.log`

### UnitTesting

**In order for tests to work properly, first purge your database** <br>
Automated Unittesting have been implemented using python's native library. Each class has been tested in a seperate file.
Test scripts can be found at `tests/` and can be run with command:<br>
`PYTHONPATH='.' coverage run tests/twitch_application_test.py`<br>
`PYTHONPATH='.' coverage run tests/<test-file-name>`<br>

To get coverage report:<br>
`coverage report -m`<br>

You can also run this from the root:<br>
`./test.sh`<br>
Then open `coverage_report.txt`

From the root directory of the project.

### Miscellaneous

We have also made a series of improvements to make the code look/read better and help with future extensibility. We:

- Created a settings.py where main parameters of the application are saved at (e.g. Top spam threshold and logger's config)
- Fixed the names of variables
- Refactored the command line argument into a separate function
- created private helper methods for connection and database changes
  - helps with error checking
