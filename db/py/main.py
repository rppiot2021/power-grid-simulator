"""
backend manager
"""

import datetime
import time

from hat import aio
from hat.event.server import common

from project.backend.db_manager import DatabaseManager
from project.backend.file_manager import FileManager

json_schema_id = None
json_schema_repo = None

db = DatabaseManager()
file = FileManager()


async def create(conf):
    backend = Backend()
    backend._async_group = aio.Group()

    backend._async_group.spawn(aio.call_on_cancel, db._close)
    backend._async_group.spawn(aio.call_on_cancel, file._close)

    return backend


class Backend(common.Backend):
    last_log_time = datetime.datetime.fromtimestamp(time.time())

    def get_file(self):
        return file

    def get_db(self):
        return db

    async def register(self, events):
        """
        middleware manager, logs into file and database with offset of 2 minutes

        """

        raw_adr = events[0].event_type[-1]

        if not raw_adr.count(";") == 1:
            return await self._async_group.spawn(aio.call, lambda: events)

        raw_adr = raw_adr.split(";")

        asdu = raw_adr[0]
        io = raw_adr[1]

        pl = events[0].payload

        val = 0 if not pl else pl.data

        current_time = datetime.datetime.fromtimestamp(time.time())
        # if current_time - datetime.timedelta(seconds=3) > Backend.last_log_time:
        if True:
            Backend.last_log_time = current_time
            current_time = datetime.datetime.fromtimestamp(time.time())

            self.get_file().write(current_time, asdu, io, val)
            self.get_db().insert_wrapper(asdu, io, val)

        return await self._async_group.spawn(aio.call, lambda: events)

    async def query(self,
                    data
                    ):
        result = []
        return await self._async_group.spawn(aio.call, lambda: result)
