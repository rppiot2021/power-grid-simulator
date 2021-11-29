# todo remove later, sim shouldn't connect to client directly
from abc import ABC, abstractmethod
import datetime
import typing

from hat.drivers import iec104


class ConnType(ABC):

    @abstractmethod
    async def connect_cb(self, connection_cb, interrogate_cb, command_cb,
                         address):
        pass

    @abstractmethod
    def wrap_data(self, simulation_data, asdu, io):
        pass

    @abstractmethod
    def wrap_value(self, value, type_104):
        pass


class ConnectionIEC104(ConnType):
    class Data(typing.NamedTuple):
        value: iec104.DataValue
        cause: iec104.Cause
        timestamp: float

    async def connect_cb(self, connection_cb, interrogate_cb, command_cb,
                         address):
        return await iec104.listen(
            connection_cb=connection_cb,
            addr=address,
            interrogate_cb=interrogate_cb,
            command_cb=command_cb
        )

    def wrap_data(self, simulation_data, asdu, io):
        return iec104.Data(asdu_address=asdu,
                           io_address=io,
                           value=simulation_data.value,
                           cause=simulation_data.cause,
                           time=iec104.time_from_datetime(
                               datetime.datetime.utcfromtimestamp(
                                   simulation_data.timestamp)),
                           quality=iec104.Quality(*([False] * 5)),
                           is_test=False)

    def wrap_value(self, value, type_104):
        if type_104 == 'float':
            return iec104.FloatingValue(value)
        if type_104 == 'single':
            return iec104.SingleValue.ON if value else iec104.SingleValue.OFF
        raise ValueError(f'{type_104}')


class ConnectionOther(ConnType):
    async def connect_cb(self, connection_cb, interrogate_cb, command_cb,
                         address):
        raise NotImplementedError

    def wrap_data(self, simulation_data, asdu, io):
        raise NotImplementedError

    def wrap_value(self, value, type_104):
        raise NotImplementedError
