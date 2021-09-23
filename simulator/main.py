import os.path
from pathlib import Path
import asyncio
import click
import datetime
import logging
import pandapower.networks
import random
import sys
import time
import typing
import math
from hat import aio
from hat import json
from hat.drivers import iec104
import hat.drivers
from hat.drivers.iec104.common import FloatingValue, SingleValue

mlog = logging.getLogger('simulator')
default_conf_path = 'conf.yaml'


class PandaPowerExample:
    # example of a simple network
    def __init__(self):
        self.net = pandapower.networks.example_simple()
        self.reference_net = self.net

    def get_ref_value(self, table, column, index):
        """

        Args:
            table: element of the network
            column: specific value that that element has
            index: which element of type 'table'

        """
        return getattr(self.net, table)[column][index]

    def get_value(self, table, column, index):
        return getattr(self.net, table)[column][index]

    def set_net_value_random(self, table, column, ref_value):
        getattr(self.net, table)[column] = max(
            random.uniform(ref_value * 0.75, ref_value * 1.25), 0)


async def async_main(conf):
    simulator = Simulator()

    simulator.pp = PandaPowerExample()

    simulator._points = conf['points']
    simulator._spontaneity = conf['spontaneity']

    address = iec104.Address(conf['address']['host'], conf['address']['port'])

    simulator._srv = await iec104.listen(
        connection_cb=simulator._connection_cb,
        addr=address,
        interrogate_cb=simulator._interrogate_cb,
        command_cb=simulator._command_cb
    )
    simulator._connections = set()

    simulator._async_group = aio.Group()
    simulator._executor = aio.create_executor()

    await simulator._executor(pandapower.runpp, simulator.pp.net)

    simulator._state = {}
    for asdu in conf['points']:
        for io in conf['points'][asdu]:
            point_conf = conf['points'][asdu][io]
            table = getattr(simulator.pp.net, point_conf['table'])
            series = table[point_conf['property']]

            simulator.push_new_value_to_state(
                asdu,
                io,
                _104_value(series[point_conf['id']], point_conf['type']),
                iec104.Cause.INITIALIZED
            )

    simulator._async_group.spawn(simulator._spontaneous_loop)

    simulator.previous = set()
    await simulator._notify()

    await simulator.wait_closed()


def check_difference(value_old, value_new):

    if isinstance(value_old, FloatingValue):
        return math.isclose(value_old.value, value_new.value, rel_tol=1e-5)
    elif isinstance(value_old, SingleValue):
        return value_old.value == value_new.value
    raise TypeError


class Simulator(aio.Resource):

    @property
    def async_group(self):
        return self._async_group

    async def _connection_cb(self, connection):
        print("connection callback CALL")
        self._connections.add(connection)
        connection.async_group.spawn(
            aio.call_on_cancel,
            lambda: self._connections.remove(connection))
        self.async_group.spawn(
            aio.call_on_cancel,
            lambda: self._connections.remove(connection))

    async def _interrogate_cb(self, _, asdu):
        data = self._data_from_state()
        if asdu == 0xFFFF:
            return data
        return [d._replace(cause=iec104.Cause.INTERROGATED_STATION)
                for d in data if d.asdu_address == asdu]

    async def _command_cb(self, _, commands):
        for command in commands:
            if command.action != iec104.Action.EXECUTE:
                mlog.warning('received action %s, only EXECUTE is supported',
                             command.action)
                continue
            conf = self._points[command.asdu_address][command.io_address]

            series = getattr(self.pp.net, conf['table'])[conf['property']]

            if conf['type'] == 'float':
                value = command.value
            elif conf['type'] == 'single':
                value = command.value == iec104.SingleValue.ON

            series[conf['id']] = value

            self.push_new_value_to_state(
                command.asdu_address,
                command.io_address,
                command.value,
                iec104.Cause.REMOTE_COMMAND
            )

        await self._notify()

        return True

    async def _spontaneous_loop(self):
        while True:
            await asyncio.sleep(random.gauss(self._spontaneity['mu'],
                                             self._spontaneity['sigma']))

            index_pool = []
            for index, _ in self.pp.net['gen'].iterrows():
                index_pool.append(index)

            index = random.choice(index_pool)
            data_point = ("gen", "p_mw")

            ref_value = self.pp.get_ref_value(*data_point, index)
            self.pp.set_net_value_random(*data_point, ref_value)

            await self._notify()

            pandapower.runpp(self.pp.net)

            for asdu in self._points:
                for io in self._points[asdu]:

                    point_conf = self._points[asdu][io]

                    table = self.pp.net[point_conf['table']]

                    series = table[point_conf['property']]

                    new_value = _104_value(series[point_conf['id']],
                                           point_conf['type'])

                    old_data = json.get(self._state, [str(asdu), str(io)])
                    old_value = old_data.value

                    if not check_difference(
                            old_value,
                            new_value
                    ):
                        self.push_new_value_to_state(
                            asdu,
                            io,
                            new_value,
                            iec104.Cause.SPONTANEOUS
                        )

    def push_new_value_to_state(self, asdu, io, value, cause):
        self._state = json.set_(
            self._state,
            [str(asdu), str(io)],
            Data(
                value=value,
                cause=cause,
                timestamp=time.time()
            )
        )

    def _data_from_state(self):
        for asdu_str, substate in self._state.items():
            for io_str, data in substate.items():
                yield _104_data(data, int(asdu_str), int(io_str))

    async def _notify(self):
        data = list(self._data_from_state())
        self._send([d for d in data if d not in self.previous])
        self.previous = set(data)

    def _send(self, data):
        for connection in self._connections:
            connection.notify_data_change(data)


class Data(typing.NamedTuple):
    value: iec104.DataValue
    cause: iec104.Cause
    timestamp: float


def _104_data(simulation_data, asdu, io):
    return iec104.Data(asdu_address=asdu,
                       io_address=io,
                       value=simulation_data.value,
                       cause=simulation_data.cause,
                       time=iec104.time_from_datetime(
                           datetime.datetime.utcfromtimestamp(
                               simulation_data.timestamp)),
                       quality=iec104.Quality(*([False] * 5)),
                       is_test=False)


def _104_value(value, type_104):
    if type_104 == 'float':
        return iec104.FloatingValue(value)
    if type_104 == 'single':
        return iec104.SingleValue.ON if value else iec104.SingleValue.OFF
    raise ValueError(f'{type_104}')


@click.command()
@click.option('--conf-path', type=Path, default=default_conf_path)
def main(conf_path):
    conf = json.decode_file(conf_path)
    aio.init_asyncio()
    aio.run_asyncio(async_main(conf))


if __name__ == '__main__':
    print("simulator started")
    sys.exit(main())
