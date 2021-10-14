"""
backend module implementation for database logging
"""

import datetime
import sqlite3
import time
from os.path import join
from shutil import copy
from pathlib import Path

from log_manager import LogManager
import yaml
import os

class DatabaseManager(LogManager):

    def __init__(
            self,
            file_path=None,
            file_folder=None,
            archive_folder=None
    ):
        with open("conf.yaml", "r") as stream:
            t = yaml.safe_load(stream)["file_manager"]

            prefix = t["prefix"]

            if prefix == "None":
                print("no prefix")

                # for joining
                prefix = ""

            else:
                print("prefix exist", prefix)

                if not os.path.exists(prefix):
                    os.makedirs(prefix)

            self.default_file_path = file_path or t["default_file_filename"]

            self.default_file_folder = file_folder or join(prefix, t[
                "default_file_folder"])
            self.default_archive_folder = archive_folder or join(prefix, t[
                "default_archive_folder"])

        Path(self.default_file_folder).mkdir(parents=True, exist_ok=True)
        Path(self.default_archive_folder).mkdir(parents=True, exist_ok=True)

        self.file_full_path = join(self.default_file_folder,
                                   self.default_file_path)

        self.file = open(self.file_full_path, "a")

        super().__init__(True)

    def _close(self):
        self.file.close()

    def write(self, *data):
        self.file.write(str(data) + "\n")

    # ///////////////////////////////////////////////////////////////////////

    def __init__(
        self,
        db_filename=None,
        index_time=180,
        log_buffer=5000,
        archive_folder=None,
        db_folder=None
    ):

        self.last_index_time = datetime.datetime.fromtimestamp(time.time())
        self.index_time = index_time
        self.log_buffer = log_buffer
        super().__init__(True)


        with open("conf.yaml", "r") as stream:
            t = yaml.safe_load(stream)["database_manager"]

            prefix = t["prefix"]

            if prefix == "None":
                print("no prefix")

                # for joining
                prefix = ""

            else:
                print("prefix exist", prefix)

                if not os.path.exists(prefix):
                    os.makedirs(prefix)

            self.default_db_path = db_filename or t["default_database_filename"]

            self.default_db_folder = db_folder or join(prefix, t[
                "default_database_folder"])
            self.default_archive_folder = archive_folder or join(prefix, t[
                "default_archive_folder"])

        Path(self.default_db_folder).mkdir(parents=True, exist_ok=True)
        Path(self.default_archive_folder).mkdir(parents=True, exist_ok=True)

        self.file_full_path = join(self.default_db_folder,
                                   self.default_db_path)

        # self.db_path = db_path
        # self.log_folder = log_folder

        # Path(log_folder).mkdir(parents=True, exist_ok=True)
        # Path(db_folder).mkdir(parents=True, exist_ok=True)

        print(f"{db_folder=}")
        print(f"{db_filename=}")

        # full_path = join(self.default_db_folder, self.d
        # )
        full_path = self.file_full_path
        self.db_full_path = full_path

        self.connection = sqlite3.connect(full_path)

        self.cursor = self.connection.cursor()

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS t
                       (date text,  
                       asdu integer, 
                       io integer,
                       value real)''')

        # Save (commit) the changes
        self.connection.commit()

    def db_wrapper(self, payload):
        self.check_connection()

        payload()

        self.connection.commit()


    def _close(self):
        """
        closes connection with database

        """

        self.check_connection()

        self.connection.close()
        self.is_opened = False

    def insert_wrapper(self, asdu, io, value):
        self._insert(asdu, io, value)

        self._indexing_handler()
        self._cleanup()

    def _cleanup(self):
        """
        create backup and empty current db

        """

        self.check_connection()

        num_of_rows = self.cursor.execute("SELECT COUNT(*) FROM t;").fetchone()[0]
        print(num_of_rows)

        if num_of_rows >= self.log_buffer:
            current_time = str(datetime.datetime.fromtimestamp(time.time())).replace(" ", "_")
            full_path = join(self.log_folder, current_time + ".db")
            open(full_path, "w+")
            copy(self.db_full_path, full_path)

            self.cursor.execute("DELETE FROM t")

        self.connection.commit()

    def _create_index(self):
        self.check_connection()

        self.cursor.execute('''DROP INDEX IF EXISTS t_index''')

        self.cursor.execute('''CREATE UNIQUE INDEX t_index ON t (asdu, io, date)''')

        # Save (commit) the changes
        self.connection.commit()

    def _indexing_handler(self):
        self.check_connection()

        current_time = datetime.datetime.fromtimestamp(time.time())

        if current_time - datetime.timedelta(seconds=self.index_time) > self.last_index_time:
            self._create_index()
            print("reindexing")
            self.last_index_time = current_time

    def _insert(self, asdu, io, value):
        """
        inserts params into database

        """
        self.check_connection()

        current_time = datetime.datetime.fromtimestamp(time.time())

        self.cursor.execute(
            f"INSERT INTO t VALUES "
            f"(\"{current_time}\", {asdu}, {io}, {value})"
        )

        self.connection.commit()

    def _custom_insert(self, table, *params):
        """
        inserts params into database

        """
        self.check_connection()

        # Insert a row of data
        self.cursor.execute("INSERT INTO " + table + " VALUES " + str(params))

        self.connection.commit()


if __name__ == '__main__':
    """"""

    with DatabaseManager() as db:
        db._insert(4, 2, 3)


    # db = DatabaseManager()
    #
    # db._cleanup()
    #
    # while True:
    #     db._insert("t", 2, 3, 2.4)
    #     db._indexing_handler()
    #     db._cleanup()

    # print(time.time())
    # current_time = datetime.datetime.fromtimestamp(time.time())
    # print(current_time)

    # create_index()
    #
    # db_init()
    # for row in cur.execute('pragma index_info("t_index")'):
    #     print(row)
    # db_close()

    # db_init()
    #
    # create_db()
    #
    # db_insert_into_t("t", 20, 4, 35.14)
    # db_insert_into_t("t", 22, 41, 33.14)
    # db_insert_into_t("t", 23, 44, 31.14)
    #
    # for row in cur.execute('select * from t'):
    #     print(row)
    #
    # db_close()
