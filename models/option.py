import datetime
import pytz
import connection_pool
import database

class Option:
    def __init__(self, option_text: str, poll_id: int, _id: int=0):
        self.id = _id
        self.text = option_text
        self.poll_id = poll_id

    def __repr__(self):
        return f"({self.text}, {self.poll_id})"

    @property
    def votes(self) -> list[database.Vote]:
        with connection_pool.get_connection() as conn:
            votes = database.get_option_votes(conn, self.id)
            return votes

    @classmethod
    def get(cls, option_id: int) -> "Option":
        with connection_pool.get_connection() as conn:
            new_option_id, new_option_text, new_option_poll_id = database.get_option(conn, option_id)
            return cls(new_option_text, new_option_poll_id, new_option_id)

    def save(self):
        with connection_pool.get_connection() as conn:
            new_option_id = database.add_poll_option(conn, self.text, self.poll_id)
            self.id = new_option_id

    def vote(self, username: str):
        with connection_pool.get_connection() as conn:
            current_datetime_utc = datetime.datetime.now(tz=pytz.utc)
            current_timestamp = current_datetime_utc.timestamp()
            database.add_option_vote(conn, username, self.id, current_timestamp)




        