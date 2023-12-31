import sqlite3 as sq
import logging
import os

from typing import Optional


"""Settings up logs for the database """
# for logging file and console output

logger_db = logging.getLogger(__name__)
logger_db.setLevel(logging.WARNING)

logger_stream_db = logging.StreamHandler()
logger_stream_db.setLevel(logging.WARNING)

handler_log_db = logging.FileHandler(f"{__name__}.log", mode="a", encoding="utf-8")
formatter_log_db = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

handler_log_db.setFormatter(formatter_log_db)
logger_db.addHandler(handler_log_db)
logger_stream_db.setFormatter(formatter_log_db)
logger_db.addHandler(logger_stream_db)


class BotDB:
    __DB_NAME = fr"{os.path.abspath(os.path.join(os.getcwd(), 'database'))}{os.path.sep}chill_base.db"

    def __init__(self):
        self.conn = sq.connect(self.__DB_NAME)
        self.cur = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cur.close()
        if isinstance(exc_val, Exception):
            self.conn.rollback()
        else:
            self.conn.commit()

        self.conn.close()

    def execute(self, sql_req, params=None):
        self.cur.execute(sql_req, params or ())

    def create_events_table(self):
        self.execute("""CREATE TABLE IF NOT EXISTS events(
                event_id INTEGER PRIMARY KEY,
                user_id INT,
                number INT,
                date DATE,
                places TEXT,
                people TEXT,
                state TEXT,
                memes TEXT
            )"""
                     )

    def alter_table(self):
        # For adding 'photos'-blob column
        self.execute("""ALTER TABLE events ADD COLUMN photos BLOB""")

    def drop_table_events(self):
        drop_req = """DROP TABLE events"""
        self.execute(drop_req)

    def insert_memo_values(self, *args: str | int) -> None:
        sql_req = """INSERT INTO events(user_id, number, date, places, people, state, memes) 
        VALUES (?, ?, ?, ?, ?, ?, ?)"""
        self.execute(sql_req, args)

    def get_new_event_number(self, user_id):
        sql_req = """SELECT number FROM events WHERE user_id =(?) ORDER BY number DESC LIMIT 1"""
        self.execute(sql_req, (user_id,))
        result = self.cur.fetchone()
        if result:
            return result[0] + 1
        else:
            return 1

    def get_exact_event_id(self, user_id, date):
        sql_req = """SELECT event_id FROM events WHERE user_id = (?) AND date = (?)"""
        self.execute(sql_req, (user_id, date))
        event_id = self.cur.fetchone()[0]
        return event_id

    def get_dates(self, user_id):
        sql_req = """SELECT date FROM events WHERE user_id=(?) ORDER BY date"""
        self.execute(sql_req, (user_id,))
        all_dates = self.cur.fetchall()
        return all_dates

    def get_dates_by_states(self, user_id, state):
        sql_req = """SELECT date FROM events WHERE user_id=(?) AND state=(?) ORDER BY date"""
        self.execute(sql_req, (user_id, state))
        all_dates_by_state = self.cur.fetchall()
        return all_dates_by_state

    def get_event_by_day(self, user_id, date):
        sql_req = """SELECT number, date, state, people, places, memes FROM events WHERE user_id = (?) AND date = (?)"""
        self.execute(sql_req, (user_id, date))
        the_event = self.cur.fetchone()
        return the_event

    def add_new_memes(self, new_memes, user_id, date) -> None:
        sql_req_fetch = """SELECT memes FROM events WHERE user_id =(?) AND date = (?)"""
        self.execute(sql_req_fetch, (user_id, date))
        fetched_memes: str = ''.join(self.cur.fetchone())

        new_and_old_memes = ";\n".join((fetched_memes, new_memes))
        sql_req = """UPDATE events SET memes = (?) WHERE user_id = (?) AND date = (?)"""
        self.execute(sql_req, (new_and_old_memes, user_id, date))

    def delete_event(self, user_id, date) -> None:
        sql_req = """DELETE FROM events WHERE user_id = (?) and date = (?)"""
        self.execute(sql_req, (user_id, date))

    def add_new_ppl(self, new_ppl, user_id, date) -> None:
        sql_req_fetch = """SELECT people FROM events WHERE user_id =(?) AND date = (?)"""
        self.execute(sql_req_fetch, (user_id, date))
        fetched_places: str = ''.join(self.cur.fetchone())

        new_and_old_ppl = "; ".join((fetched_places, new_ppl))
        sql_req = """UPDATE events SET people = (?) WHERE user_id = (?) AND date = (?)"""
        self.execute(sql_req, (new_and_old_ppl, user_id, date))

    def add_new_places(self, new_places, user_id, date) -> None:
        sql_req_fetch = """SELECT places FROM events WHERE user_id =(?) AND date = (?)"""
        self.execute(sql_req_fetch, (user_id, date))
        fetched_places: str = ''.join(self.cur.fetchone())

        new_and_old_places = "; ".join((fetched_places, new_places))
        sql_req = """UPDATE events SET places = (?) WHERE user_id = (?) AND date = (?)"""
        self.execute(sql_req, (new_and_old_places, user_id, date))

    def update_photo_column(self, user_id, date, photo_id) -> None:
        sql_req = """UPDATE events SET photos = (?) WHERE user_id = (?) AND date = (?) """
        self.execute(sql_req, (photo_id, user_id, date))

    def add_new_photo(self, user_id, date, new_photo_id) -> None:
        sql_req_fetch = """SELECT photos FROM events WHERE user_id = (?) AND date = (?)"""
        self.execute(sql_req_fetch, (user_id, date))
        old_photos = self.cur.fetchone()

        if old_photos[0]:
            old_photos_prepared = ''.join(old_photos)

            new_and_old_photos = ", ".join((old_photos_prepared, new_photo_id))
            sql_req_upd = """UPDATE events SET photos = (?) WHERE user_id = (?) AND date = (?)"""
            self.execute(sql_req_upd, (new_and_old_photos, user_id, date))

        else:
            self.update_photo_column(user_id=user_id, date=date, photo_id=new_photo_id)

    def get_photo(self, user_id, date):
        sql_req = """SELECT photos FROM events WHERE user_id = (?) AND date = (?)"""
        self.execute(sql_req, (user_id, date))
        photo_id = self.cur.fetchone()
        if not photo_id:
            return None
        elif photo_id[0]:
            prep_photo_id = tuple(photo_id[0].split(', '))

            return prep_photo_id


class RickDB(BotDB):
    @classmethod
    def pages_sorter(cls, unready_pages: str):
        """
        convert string to list of integers, sort them, and convert them back
        :param unready_pages: string of pages
        :return: string of sorted pages to the table of Ricquotes
        """
        sorted_int_pages = sorted(list(map(int, unready_pages.split())))
        return " ".join(map(str, sorted_int_pages))

    def create_rick_quotes_table(self) -> None:
        """Creating a table for making quotes of a great Rich Sanchez (from any Universe)"""
        self.execute("""CREATE TABLE IF NOT EXISTS rick_quotes(
                        pages TEXT
                    )"""
                     )

    def update_pages(self, pages: str) -> None:
        """Updating seen pages from the book"""
        self.execute("""SELECT pages FROM rick_quotes""")
        seen_pages: tuple = self.cur.fetchone()

        if not seen_pages:
            sql_req = """INSERT INTO rick_quotes(pages) VALUES (?)"""
            ready_pages = self.pages_sorter(pages)
            self.execute(sql_req=sql_req, params=(ready_pages, ))
        else:
            self.execute("""SELECT pages FROM rick_quotes""")
            fetched_pages = self.cur.fetchone()[0]
            concatenation = " ".join((fetched_pages, pages))
            ready_concatenation = self.pages_sorter(concatenation)

            sql_req = """UPDATE rick_quotes SET pages = (?) """
            self.execute(sql_req=sql_req, params=(ready_concatenation, ))

    def get_pages(self) -> Optional[str]:
        try:
            self.execute("""SELECT pages FROM rick_quotes""")
            fetched_pages = self.cur.fetchone()[0]

            return fetched_pages

        except TypeError:
            # if db fetches 'None'
            logger_db.warning("Ricquotes are empty")
            return None



