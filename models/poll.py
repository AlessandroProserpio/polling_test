from models.option import Option
import connection_pool
import database

class Poll:
    def __init__(self,text: str,owner: str,_id: int=0):
        self.id = _id
        self.text = text
        self.owner = owner

    def __repr__(self) -> str:
        return f"({self.id}, {self.text}, {self.owner})"

    @property
    def options(self) -> list[Option]:
        with connection_pool.get_connection() as conn:
            options = database.get_options(conn, self.id)
            return [Option(option_text, option_poll_id, option_id) for option_id, option_text, option_poll_id in options]

    @classmethod
    def get(cls, poll_id: int) -> 'Poll':
        with connection_pool.get_connection() as conn:
            _id, poll_text, poll_owner = database.get_poll(conn, poll_id)
            return cls(poll_text, poll_owner, _id)

    @classmethod
    def get_all(cls) -> list['Poll']:
        with connection_pool.get_connection() as conn:
            polls = database.get_polls(conn)
            return [cls(poll_text, poll_owner, poll_id) for poll_id, poll_text, poll_owner in polls]

    @classmethod
    def get_latest(cls) -> "Poll":
        with connection_pool.get_connection() as conn:
            poll_id, poll_text, poll_owner = database.get_latest_poll(conn)
            return cls(poll_text, poll_owner, poll_id)

    def save(self):
        with connection_pool.get_connection() as conn:
            new_poll_id = database.create_poll(conn, self.text, self.owner)
            self.id = new_poll_id

    def add_option(self, option_text: str):
        Option(option_text, self.id).save()

