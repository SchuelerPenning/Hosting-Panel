from os import getenv
from uuid import uuid4, UUID
from datetime import datetime, timedelta

from mysql import connector

from models.user import User
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

        query = "INSERT INTO sessions (session_id, user_id, created_at, expires_at, session_data) VALUES (%s, %s, %s, %s, %s);"
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
        query = "SELECT * FROM sessions WHERE session_id = %s AND expires_at > NOW();"
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
        query = "UPDATE sessions SET session_data = %s WHERE session_id = %s;"
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
        query = "UPDATE sessions SET expires_at = %s WHERE session_id = %s;"
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
        query = "DELETE FROM sessions WHERE session_id = %s;"
        with self.get_cursor() as cursor:
            cursor.execute(query, (session_id,))
        self.connection.commit()

    def validate_session(self, session_id: UUID) -> bool:
        """
        Checks if a session exists and is not expired
        :param session_id:
        :return:
        """
        query = "SELECT * FROM sessions WHERE session_id = %s and expires_at < NOW();"
        values = (session_id,)
        with self.get_cursor() as cursor:
            cursor.execute(query, values)
            results = cursor.fetchall()
        return True if results else False

    def create_user(self, username: str, email: str, firstname: str, lastname: str, street: str, number: str,
                    postcode: str, city: str, country: str, password_hash: str) -> None:
        """
        Creates a new user in the database the specified data
        :param username:
        :param email:
        :param firstname:
        :param lastname:
        :param street:
        :param number:
        :param postcode:
        :param city:
        :param country:
        :param password_hash:
        :return:
        """
        query_users = "INSERT INTO users (username, email, firstname, lastname, street, number, postcode, city, country) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"
        values_users = (username, email, lastname, firstname, street, number, postcode, city, country)
        with self.get_cursor() as cursor:
            cursor.execute(query_users, values_users)
            cursor.execute("SELECT id FROM users WHERE username = %s;", (username,))
            user_id = cursor.fetchone()[0]
        query_auth = "INSERT INTO auth (id, username, email, password) VALUES (%s, %s, %s, %s);"
        values_auth = (user_id, username, email, password_hash)
        with self.get_cursor() as cursor:
            cursor.execute(query_auth, values_auth)

    def update_user(self, modified_user: User) -> None:
        """
        Updates the specified user in the database
        :param modified_user:
        :return:
        """
        query = """
            UPDATE users
            SET username = %s, email = %s, firstname = %s, lastname = %s, role = %s, street = %s, number = %s, postcode = %s, city = %s, country = %s
            WHERE id = %s;
        """
        values = (
            modified_user.username,
            modified_user.email,
            modified_user.firstname,
            modified_user.lastname,
            modified_user.role,
            modified_user.street,
            modified_user.number,
            modified_user.postcode,
            modified_user.city,
            modified_user.country,
            modified_user.user_id
        )
        with self.get_cursor() as cursor:
            cursor.execute(query, values)

    def delete_user(self, user_id: int) -> None:
        """
        Deletes the user with the specified id form the database
        :param user_id:
        :return:
        """
        query = "DELETE FROM users WHERE user_id = %s;"
        values = (user_id,)
        with self.get_cursor() as cursor:
            cursor.execute(query, values)

    def fetch_user(self, user_id: int) -> User | None:
        """
        Fetches a user by his id from the database
        :param user_id:
        :return:
        """
        query = "SELECT * FROM users WHERE user_id = %s;"
        values = (user_id,)
        with self.get_cursor() as cursor:
            cursor.execute(query, values)
        return cursor.fetchone()

    def disable_user(self, user_id: int) -> None:
        """
        Sets a user's state to disabled; revokes the ability to act for that user
        :param user_id:
        :return:
        """
        query = "UPDATE users SET state = 'disabeld' WHERE user_id = %s;"
        values = (user_id,)
        with self.get_cursor() as cursor:
            cursor.execute(query, values)

    def authenticate_credentials(self, email: str, password_hash: str) -> int:
        """
        Checks if the given credentials are in the database and returns the user's ID
        :param email:
        :param password_hash:
        :return:
        """
        query = "SELECT id FROM users WHERE email = %s AND password_hash = %s;"
        values = (email, password_hash)
        with self.get_cursor() as cursor:
            cursor.execute(query, values)
            all_results = cursor.fetchall()
        return all_results[0] if len(all_results) == 1 else -1
