from os import getenv
from uuid import uuid4, UUID
from datetime import datetime, timedelta

from mysql import connector

from cursor import DBCursor


class DatabaseHandler:
    def __init__(self):
        self.host = getenv("DATABASE.HOST")
        self.user = getenv("DATABASE.USER")
        self.password = getenv("DATABASE.PASSWORD")
        self.database_name = getenv("DATABASE.DBNAME")

        self.connection = connector.connect(
            self.host,
            self.user,
            self.password,
            self.database_name
        )

    def get_cursor(self) -> DBCursor:
        """
        Returns a modified Database cursor to allow the usage of a context manager
        :return:
        """
        return DBCursor(self.connection.cursor())

    def create_session(self, user_id: int, session_data: str, session_duration=3600) -> str:
        """
        Creates a new session and stores it in the database
        :param user_id:
        :param session_data:
        :param session_duration:
        :return:
        """
        session_id = str(uuid4())
        created_at = datetime.now()
        expires_at = created_at + timedelta(seconds=session_duration)

        query = "INSERT INTO sessions (session_id, user_id, created_at, expires_at, session_data) VALUES (%s, %s, %s, %s, %s)"
        values = (session_id, user_id, created_at, expires_at, session_data)
        with self.get_cursor() as cursor:
            cursor.execute(query, values)
        self.connection.commit()

        return session_id

    def retrieve_session(self, session_id: UUID) -> tuple:
        """
        Queries the session for the given session_id from the database
        :param session_id:
        :return:
        """
        query = "SELECT * FROM sessions WHERE session_id = %s AND expires_at > NOW()"
        with self.get_cursor() as cursor:
            cursor.execute(query, (session_id,))
        session = cursor.fetchone()
        return session

    def update_session(self, session_id: UUID, session_data: str) -> None:
        """
        Updates the session for the given session_id with the new session data
        :param session_id:
        :param session_data:
        :return:
        """
        updated_at = datetime.now()
        query = "UPDATE sessions SET session_data = %s WHERE session_id = %s"
        values = (session_data, updated_at, session_id)
        with self.get_cursor() as cursor:
            cursor.execute(query, values)
        self.connection.commit()

    def refresh_session(self, session_id: UUID, new_expires_at: datetime) -> None:
        """
        Refreshes the session for the given session_id to expire at the new given expiration date
        :param session_id:
        :param new_expires_at:
        :return:
        """
        query = "UPDATE sessions SET expires_at = %s WHERE session_id = %s"
        values = (new_expires_at, session_id)
        with self.get_cursor() as cursor:
            cursor.execute(query, values)
        self.connection.commit()

    def delete_session(self, session_id: UUID) -> None:
        """
        Deletes a session from the database
        :param session_id:
        :return:
        """
        query = "DELETE FROM sessions WHERE session_id = %s"
        with self.get_cursor() as cursor:
            cursor.execute(query, (session_id,))
        self.connection.commit()

    def create_user(self, username: str, email: str, firstname: str, lastname: str, street: str, number: str, postcode: str, city: str, country: str) -> None:
        pass
