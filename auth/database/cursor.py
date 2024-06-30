from mysql.connector.cursor import MySQLCursorAbstract


class DBCursor:
    def __init__(self, cursor: MySQLCursorAbstract):
        self.c = cursor

    def __enter__(self):
        return self.c

    def __exit__(self, exc_type, exc_value, traceback):
        return self.c.close()
