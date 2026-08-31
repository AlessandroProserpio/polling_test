from connection_pool import get_cursor

############### DATA TYPES ###############
Poll = tuple[int, str, str]
Option = tuple[int, str, int]
Vote = tuple[str, int, float|int]


############################## QUERIES ##########################
## -- create
CREATE_POLLS = """CREATE TABLE IF NOT EXISTS polls (
                                                id SERIAL PRIMARY KEY,
                                                title TEXT,
                                                owner TEXT);"""
CREATE_OPTIONS = """CREATE TABLE IF NOT EXISTS options(
                                                id SERIAL PRIMARY KEY,
                                                option_text TEXT,
                                                poll_id INTEGER,
                                                FOREIGN KEY (poll_id) REFERENCES polls (id)
                                                );"""
CREATE_VOTES = """CREATE TABLE IF NOT EXISTS votes (
                                            username TEXT,
                                            option_id INTEGER,
                                            vote_timestamp INTEGER,
                                            FOREIGN KEY (option_id) REFERENCES options (id)
                                            );"""

## -- insert
INSERT_POLL = """INSERT INTO polls (title, owner) VALUES (%s,%s) RETURNING id;"""
INSERT_OPTION = """INSERT INTO options (option_text, poll_id) VALUES (%s,%s) RETURNING id;"""
INSERT_VOTE = """INSERT INTO votes (username, option_id, vote_timestamp) VALUES (%s,%s,%s);"""

## -- select
SELECT_POLLS = "SELECT * FROM polls;"
SELECT_POLL = "SELECT * FROM polls WHERE id = %s;"
SELECT_LATEST_POLL = """SELECT * FROM polls WHERE id = ( SELECT id FROM polls ORDER BY id DESC LIMIT 1 );"""
SELECT_OPTION = "SELECT * FROM options WHERE id = %s;"
SELECT_POLL_OPTIONS = "SELECT * FROM options WHERE poll_id = %s;"
SELECT_VOTES_FOR_OPTION = "SELECT * FROM votes WHERE votes.option_id = %s;"

def create_tables(conn):
    with get_cursor(conn) as cursor:
        cursor.execute(CREATE_POLLS)
        cursor.execute(CREATE_OPTIONS)
        cursor.execute(CREATE_VOTES)

## -- pools
def create_poll(conn, poll_text: str, poll_owner: str) -> int:
    with get_cursor(conn) as cursor:
        cursor.execute(INSERT_POLL, (poll_text, poll_owner))
        new_poll_id = cursor.fetchone()[0]
        return new_poll_id

def get_poll(conn, pool_id: int) -> Poll:
    with get_cursor(conn) as cursor:
        cursor.execute(SELECT_POLL, (pool_id,))
        return cursor.fetchone()

def get_polls(conn) -> list[Poll]:
    with get_cursor(conn) as cursor:
        cursor.execute(SELECT_POLLS)
        return cursor.fetchall()

def get_latest_poll(conn) -> Poll:
    with get_cursor(conn) as cursor:
        cursor.execute(SELECT_LATEST_POLL)
        return cursor.fetchone()

## -- options
def get_option(conn, option_id: int) -> Option:
    with get_cursor(conn) as cursor:
        cursor.execute(SELECT_OPTION, (option_id,))
        return cursor.fetchone()

def get_options(conn, poll_id: int) -> list[Option]:
    with get_cursor(conn) as cursor:
        cursor.execute(SELECT_POLL_OPTIONS, (poll_id,))
        return cursor.fetchall()

def add_poll_option(conn, text: str, option_id: int) -> int:
    with get_cursor(conn) as cursor:
        cursor.execute(INSERT_OPTION, (text, option_id))
        new_option_id = cursor.fetchone()[0]
        return new_option_id


### -- votes
def get_option_votes(conn, option_id: int) -> list[Vote]:
    with get_cursor(conn) as cursor:
        cursor.execute(SELECT_VOTES_FOR_OPTION, (option_id,))
        return cursor.fetchall()

def add_option_vote(conn, username: str, option_id: int, timestamp: float):
    with get_cursor(conn) as cursor:
        cursor.execute(INSERT_VOTE, (username, option_id, timestamp))