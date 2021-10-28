"""
backend manager
"""

import datetime
import time
from enum import Enum

from hat import aio
from hat.aio import run_asyncio

from db_manager import DatabaseManager
from file_manager import FileManager

import atexit

class LogType(Enum):
    DB = 0  # Database
    FILE = 1  # File


class LogInterface:
    # last_log_time = datetime.datetime.fromtimestamp(time.time())

    def __init__(self):
        self.last_log_time = datetime.datetime.fromtimestamp(time.time())
        self.db = DatabaseManager()
        self.file = FileManager()

        self.db_last_log_time = datetime.datetime.fromtimestamp(time.time())
        self.file_last_log_time = datetime.datetime.fromtimestamp(time.time())

        # todo test this
        atexit.register(self.db._close)
        atexit.register(self.file._close)

    def file_write(self, *data):

        current_time = datetime.datetime.fromtimestamp(time.time())

        # if True:
        if current_time - datetime.timedelta(seconds=3) > self.file_last_log_time:
            self.file_last_log_time = current_time

            self.file.write(data)

            print("log")

        else:
            print("ignore")

    def db_write(self, asdu, io, value):

        current_time = datetime.datetime.fromtimestamp(time.time())

        # if True:
        if current_time - datetime.timedelta(seconds=3) > self.db_last_log_time:
            self.db_last_log_time = current_time

            self.db.insert(asdu, io, value)

    def db_custom_insert(self, table, *params):

        current_time = datetime.datetime.fromtimestamp(time.time())

        # if True:
        if current_time - datetime.timedelta(seconds=3) > self.db_last_log_time:
            self.db_last_log_time = current_time

            self.db.custom_insert(table, params)


# class Tmp:
#     def __init__(self):
#         print("created")
#
# async def create(obj):
#
#     c_obj = obj()
#
#     c_obj._async_group = aio.Group()
#
#     db_manager = DBManager()
#
#     c_obj._async_group.spawn(aio.call_on_cancel, db_manager.db._close)
#     c_obj._async_group.spawn(aio.call_on_cancel, db_manager.file._close)
#
#     print("created")
#
#     return c_obj

async def async_main():

    log_interface = LogInterface()

    i = 0

    while True:
        i += 1

        log_interface.file_write("bla bla bla")
        time.sleep(1)

def main():
    run_asyncio(async_main())


if __name__ == '__main__':
    main()
