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
        db_filename=None,
        index_time=180,
        log_buffer=5000,
        archive_folder=None,
        db_folder=None
    ):

        self.last_index_time = datetime.datetime.fromtimestamp(time.time())
        self.index_time = index_time
        self.log_buffer = log_buffer

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

        self.db_full_path = join(self.default_db_folder, self.default_db_path)

        self.connection = sqlite3.connect(self.db_full_path)

        self.cursor = self.connection.cursor()

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS t
                       (date text,  
                       asdu integer, 
                       io integer,
                       value real)''')

        # Save (commit) the changes
        self.connection.commit()

    def _close(self):
        """
        closes connection with database

        """

        self.connection.close()

    def insert(self, asdu, io, value):
        self._insert(asdu, io, value)

        self._indexing_handler()
        self._cleanup()

    def _insert(self, asdu, io, value):
        """
        inserts defined params into table
        """

        current_time = datetime.datetime.fromtimestamp(time.time())

        self.cursor.execute(
            f"INSERT INTO t VALUES "
            f"(\"{current_time}\", {asdu}, {io}, {value})"
        )

        self.connection.commit()

    def custom_insert(self, table, *params):
        self._custom_insert(table, params)

        self._indexing_handler()
        self._cleanup()

    def _custom_insert(self, table, *params):
        """
        inserts custom @params into custom @table
        """

        # Insert a row of data
        self.cursor.execute("INSERT INTO " + table + " VALUES " + str(params))

        self.connection.commit()

    def _indexing_handler(self):
        """
        reindex if @self.last_index_time has exceeded
        """

        current_time = datetime.datetime.fromtimestamp(time.time())

        if current_time - datetime.timedelta(seconds=self.index_time) > self.last_index_time:
            self._create_index()
            print("reindexing")
            self.last_index_time = current_time

    def _create_index(self):
        """
        create index
        handle existing index
        """

        self.cursor.execute('''DROP INDEX IF EXISTS t_index''')

        self.cursor.execute('''CREATE UNIQUE INDEX t_index ON t (asdu, io, date)''')

        # Save (commit) the changes
        self.connection.commit()

    def _cleanup(self):
        """
        create backup of current state of db and empty current db
        """

        num_of_rows = self.cursor.execute("SELECT COUNT(*) FROM t;").fetchone()[0]
        print(num_of_rows)

        if num_of_rows >= self.log_buffer:
            current_time = str(datetime.datetime.fromtimestamp(time.time())).replace(" ", "_")
            full_path = join(self.default_archive_folder, current_time + ".db")
            open(full_path, "w+")
            copy(self.db_full_path, full_path)

            self.cursor.execute("DELETE FROM t")

        self.connection.commit()


if __name__ == '__main__':

    with DatabaseManager(index_time=5) as db:

        while True:
            time.sleep(1)
            # db.insert(4, 2, 3)
            db.custom_insert("t", 3, 5, 2, 3)
