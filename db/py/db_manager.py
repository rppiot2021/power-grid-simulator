"""
backend module implementation for database logging
"""

import datetime
import random
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
        index_time=180,
        log_buffer=5000,
        prefix=None,
        db_filename=None,
        archive_folder=None,
        db_folder=None
    ):
        """

        :param index_time: time between reindexing
        :param log_buffer: archive current state of database after this
        number of logs has exceeded
        :param db_filename:
        :param archive_folder:
        :param db_folder:
        """

        self.last_index_time = datetime.datetime.fromtimestamp(time.time())
        self.index_time = index_time
        self.log_buffer = log_buffer

        super().__init__("database_manager", prefix, db_folder, db_filename, archive_folder)

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
        self.cursor.execute("INSERT INTO " + table + " VALUES " + str(params[0]))

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
            db.insert(4, 2, 3)
            db.custom_insert("t", 4, 5, 2, 3)
