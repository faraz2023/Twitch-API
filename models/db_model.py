import sqlite3
import settings

class DbHandler():

    # SINGLETON PATTERN
    __instance = None
    def __init__(self, database_name):

        if DbHandler.__instance == None:
            self.database_name = database_name
            self.logger = settings.db_logger

            try:
                # set up twitch database
                self.set_up_twitch_db()
                self.logger.info('Database ({}) set up complete'.format(self.database_name))
            except sqlite3.DatabaseError as e:# pragma: no cover
                self.logger.error('Database ({}) set up failed.\n\tError: {}'.format(self.database_name, e))

            DbHandler.__instance = self
        else:
            raise TypeError("DbHandler model cannot have multiple instances")

    @staticmethod
    def getInstance():
        return DbHandler.__instance


    # Set up databse with necessary tables for the twich application
    def set_up_twitch_db(self):
        connection = self.__open_connection()

        # Check that connection is made
        if connection:
            cursor = self.__get_cursor(connection)
        else:
            raise sqlite3.DatabaseError("Could not connect to database")

        create_tables_query = '''
            CREATE TABLE if not exists channels
            (channel_id integer primary key, channel_name text);

            PRAGMA foreign_keys = ON;

            CREATE TABLE if not exists top_spam (channel_id integer NOT NULL,
            stream_id integer NOT NULL, spam_text string, spam_occurrences integer, spam_user_count integer, FOREIGN KEY(channel_id) REFERENCES channels(channel_id));

            CREATE TABLE if not exists chat_log (channel_id integer NOT NULL,
            stream_id integer NOT NULL, text string, user string, chat_time datetime,
            offset int, FOREIGN KEY(channel_id) REFERENCES channels(channel_id));
        '''

        if not self.__execute_multiple_query(cursor, create_tables_query):
            raise sqlite3.DatabaseError("Could not query database")# pragma: no cover

        if not self.__commit(connection):
            raise sqlite3.DatabaseError("Could not commit to database")# pragma: no cover

        self.__close_connection(connection)


    # Insert list of values into table table_name
    def insert_values(self, table_name, values):

        connection = self.__open_connection()

        # Check that connection is made
        if connection:
            cursor = self.__get_cursor(connection)
        else:
            raise sqlite3.DatabaseError("Could not connect to database")# pragma: no cover

        # Generate query with correct number of arguments
        query = "INSERT INTO " + table_name + " VALUES("
        for index in range(len(values)):
            query += '?,'
        query = query[:-1]
        query += ')'

        if not self.__execute_query_values(cursor, query, values):
            raise sqlite3.DatabaseError("Could not insert to database")

        if not self.__commit(connection):
            raise sqlite3.DatabaseError("Could not commit to database")# pragma: no cover

        self.__close_connection(connection)
        self.logger.info('Database ({}) insert to {} complete'.format(self.database_name, table_name))


    # values must be a list of (list of insert values)
    # Raises error on failures that do not affect insert, returns number of failures
    def insert_multiple_values(self, table_name, values):

        connection = self.__open_connection()

        # Check that connection is made
        if connection:
            cursor = self.__get_cursor(connection)
        else:
            raise sqlite3.DatabaseError("Could not connect to database")# pragma: no cover

        not_inserted = 0
        for value in values:
            # Generate query with correct number of arguments
            query = "INSERT INTO " + table_name + " VALUES("

            # Construct the rest of the query
            for index in range(len(value)):
                query += '?,'
            query = query[:-1]
            query += ')'

            # If couldn't be added to database, count and move to next
            if not self.__execute_query_values(cursor, query, value):
                not_inserted += 1

        if not self.__commit(connection):
            raise sqlite3.DatabaseError("Could not commit to database")# pragma: no cover

        self.__close_connection(connection)

        if not_inserted > 0:
            self.logger.info('Database ({}) inserted {} values into {} but failed \
            to insert {} values'.format(self.database_name, len(values) - not_inserted, table_name, not_inserted))
        else:
            self.logger.info('Database ({}) insert {} values to {} complete'.format(self.database_name, len(values), table_name))

        return not_inserted


    def delete_from_database(self, table_name, conditions=[], and_or='AND'):
        # Set and_or to default if correct options not provided
        if and_or != 'AND' or and_or != 'OR':
            and_or = 'AND'

        query = 'DELETE FROM ' + table_name + ' WHERE '

        if conditions == []:
            raise sqlite3.DatabaseError("Invalid syntax: conditions must be provided")

        invalid_condition_count = 0
        for index, condition in enumerate(conditions):
            # Check that condition is in valid format
            if not isinstance(condition, str) or len(condition.split(' ')) != 3:
                invalid_condition_count += 1
                continue
            else:
                condition_str = self.__condition_to_sql_str(condition)

                # Check if more conditions
                if index < len(conditions) - 1:
                    condition_str += ' ' + and_or + ' '

                query += condition_str

        # Check if no conditions got added
        if conditions != [] and invalid_condition_count == len(conditions):
            raise sqlite3.DatabaseError("Invalid syntax: valid conditions must be provided")

        # Connect to database
        connection = self.__open_connection()

        # Check that connection is made
        if connection:
            cursor = self.__get_cursor(connection)
        else:
            raise sqlite3.DatabaseError("Could not connect to database")# pragma: no cover

        self.__execute_select_query(cursor, query)

        if not self.__commit(connection):
            raise sqlite3.DatabaseError("Could not commit to database")# pragma: no cover

        self.__close_connection(connection)

        return invalid_condition_count


    # Query the database and return result as a list of dicts{column<key>: value<value>}
    # where each dict is a row in the database
    #
    # Parameters:
    # table_name<str>: name of the table to query
    # columns<list of str>: name of columns to be returned; '*' for all columns
    # conditions<list of str>: list of conditions in string representation for the query
    #  -> string in condition must be in the following format:
    #     "COLUMN_NAME [ eq | gt | lt| gteq | lteq | like ] VLAUE"
    def select_from_database(self, table_name, columns=['*'], conditions=[], and_or='AND', \
        order_by='', ASC_DESC='', group_by=''):

        # Set and_or to default if correct options not provided
        if and_or != 'AND' and and_or != 'OR':
            and_or = 'AND'

        query = 'SELECT '

        for column_name in columns:
            if column_name == '*' and len(columns) != 1:
                raise sqlite3.DatabaseError("Invalid syntax: catch all with multiple columns")
            query += column_name + ','
        # remove last ',' from query
        query = query[:-1]

        query += ' FROM ' + table_name

        if conditions != []:
            WHERE_STATEMENT = ' WHERE '
            query += WHERE_STATEMENT

        invalid_condition_count = 0
        for index, condition in enumerate(conditions):
            # Check that condition is in valid format
            if not isinstance(condition, str) or len(condition.split(' ')) != 3:
                invalid_condition_count += 1
                # Remove and_or if at end of query
                if query[len(query) - len(and_or) - 2:] == (' ' + and_or + ' '):
                    # +2 for empty space around AND_OR
                    query = query[:len(query)-(len(and_or) + 2)]
                continue
            else:
                condition_str = self.__condition_to_sql_str(condition)


                # Check if more conditions
                if index < len(conditions) - 1:
                    condition_str += ' ' + and_or + ' '

                query += condition_str


        # Check if no conditions got added
        if conditions != [] and invalid_condition_count == len(conditions):
            # remove WHERE statement
            query = query[:len(query)-len(WHERE_STATEMENT)]

        # Only group results if group by column(s) provided in form of string
        if group_by != '' and isinstance(group_by, str):
            query += ' GROUP BY ' + group_by

        # Only order results if order by column(s) provided in form of string
        if order_by != '' and isinstance(order_by, str):
            query += ' ORDER BY ' + order_by + ' ' + ASC_DESC

        # Connect to database
        connection = self.__open_connection()

        # Check that connection is made
        if connection:
            cursor = self.__get_cursor(connection)
        else:
            raise sqlite3.DatabaseError("Could not connect to database")# pragma: no cover

        results = self.__execute_select_query(cursor, query)

        if not results:
            raise sqlite3.DatabaseError("Could not query the database")

        # Get names of columns selected
        column_names = [name[0] for name in cursor.description]

        list_of_rows = []
        for row in results:
            row_dict = {}
            # Get required column values and add it to dict for results
            for index, name, in enumerate(column_names):
                row_dict[name] = row[index]
            list_of_rows.append(row_dict)

        self.__close_connection(connection)

        return list_of_rows


    # take condition string with user provided condition and convert to sql
    def __condition_to_sql_str(self, condition):

        [column, operator, value] = condition.split(' ')

        condition_str = column
        # Put condition into correct sql syntax
        if operator == "eq":
            condition_str += " = " + value
        elif operator == "gt":
            condition_str += " > " + value
        elif operator == "lt":
            condition_str += " < " + value
        elif operator == "gteq":
            condition_str += " >= " + value
        elif operator == "lteq":
            condition_str += " <= " + value
        elif operator == "like":
            condition_str += " like " + value

        return condition_str


    # Opens connection to databse
    # returns connection on success or None on failure
    def __open_connection(self):
        try:
            connection = sqlite3.connect(self.database_name)
            self.logger.info('Database ({}) connection opened'.format(self.database_name))
            return connection
        except TypeError as e:
            # log Error
            self.logger.error('Database ({}) connection open failed'.format(self.database_name))
            return None


    def __close_connection(self, connection):
        connection.close()


    def __get_cursor(self, connection):
        return connection.cursor()


    def __execute_select_query(self, cursor, query):
        try:
            result = cursor.execute(query)
            self.logger.info('Database ({}) executed select command successfully'.format(self.database_name))
            return result
        except sqlite3.DatabaseError as e:
            # log Error
            self.logger.error('Database ({}) select execution failed.\n\tError: {}'.format(self.database_name, e))
            return None


    # Execute query with values
    # returns Boolean: True on success, False on failure
    def __execute_query_values(self, cursor, query, values):
        try:
            cursor.execute(query, values)
            return True
        except sqlite3.DatabaseError as e:
            # log Error
            self.logger.error('Database ({}) execution failed.\n\tError: {}'.format(self.database_name, e))
            return False


    # Execute multiple provided queries
    # returns Boolean: True on success, False on failure
    def __execute_multiple_query(self, cursor, query):
        try:
            cursor.executescript(query)
            self.logger.info('Database ({}) executed command successfully'.format(self.database_name))
            return True
        except sqlite3.DatabaseError as e:# pragma: no cover
            # log Error
            self.logger.error('Database ({}) execution failed.\n\tError: {}'.format(self.database_name, e))
            return False


    # Commit any changes to database provided connection
    # returns Boolean: True on success, False on failure
    def __commit(self, connection):
        try:
            connection.commit()
            self.logger.info('Database ({}) committed successfully'.format(self.database_name))
            return True
        except sqlite3.DatabaseError as e:# pragma: no cover
            self.logger.error('Database ({}) commit failed.\n\tError: {}'.format(self.database_name, e))
            return False
