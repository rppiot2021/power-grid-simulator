import time
import asyncio
import random
import pandapower.networks
import logging
from hat import aio
from hat.drivers import iec104
from hat import json

mlog = logging.getLogger('simulator')


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


class Simulator(aio.Resource):

    @property
    def async_group(self):
        return self._async_group

    async def _connection_cb(self, connection):
        # gets iec104 connection object
        self._connections.add(connection)

        for i in [connection, self]:
            i.async_group.spawn(
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
            # todo iec
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

            self._push_new_value_to_state(
                command.asdu_address,
                command.io_address,
                command.value,
                iec104.Cause.REMOTE_COMMAND)

        await self._notify()

        return True

    async def _loop_driver(self, payloader):
        for asdu in self._points:
            for io in self._points[asdu]:
                point_conf = self._points[asdu][io]
                table = self.pp.net[point_conf['table']]
                series = table[point_conf['property']]

                await payloader(
                    asdu=asdu,
                    io=io,
                    point_conf=point_conf,
                    series=series
                )

    async def _loop_init_payload(self, asdu, io, point_conf, series):

        self._push_new_value_to_state(
            asdu,
            io,
            self._protocol.wrap_value(series[point_conf['id']],
                                      point_conf['type']),
            iec104.Cause.INITIALIZED)

    async def _loop_while_payload(self, asdu, io, point_conf, series):

        old_value = json.get(self._state, [str(asdu), str(io)]).value

        new_val = self._protocol.wrap_value(series[point_conf['id']],
                                            point_conf['type'])

        if not old_value.value == new_val.value:
            self._push_new_value_to_state(
                asdu, io, new_val, iec104.Cause.SPONTANEOUS)

    async def _main_loop(self):

        await self._loop_driver(self._loop_init_payload)

        while True:
            await asyncio.sleep(random.gauss(self._spontaneity['mu'],
                                             self._spontaneity['sigma']))

            index_pool = [index for index, _ in self.pp.net['gen'].iterrows()]

            index = random.choice(index_pool)
            data_point = ("gen", "p_mw")

            ref_value = self.pp.get_ref_value(*data_point, index)
            self.pp.set_net_value_random(*data_point, ref_value)

            await self._notify()

            pandapower.runpp(self.pp.net)

            await self._loop_driver(self._loop_while_payload)

    def _push_new_value_to_state(self, asdu, io, value, cause):
        self._state = json.set_(
            self._state,
            [str(asdu), str(io)],
            self._protocol.Data(
                value=value,
                cause=cause,
                timestamp=time.time()))
        global callback_new_value
        callback_new_value([str(asdu), str(io)])

    def _data_from_state(self):
        for asdu_str, substate in self._state.items():
            for io_str, data in substate.items():
                yield self._protocol.wrap_data(data, int(asdu_str),
                                               int(io_str))

    async def _notify(self):

        data = list(self._data_from_state())
        self._send([d for d in data if d not in self.previous])
        self.previous = set(data)

        global callback_notify
        callback_notify(data)

    def _send(self, data):
        for connection in self._connections:
            connection.notify_data_change(data)


callback_new_value = None
callback_notify = None


async def run_sim(conf, protocol, callback_notif, callback_new_val):
    global callback_new_value
    callback_new_value = callback_new_val
    global callback_notify
    callback_notify = callback_notif

    simulator = Simulator()
    simulator._state = {}
    simulator.pp = PandaPowerExample()

    simulator._points = conf['points']
    simulator._spontaneity = conf['spontaneity']

    address = iec104.Address(conf['address']['host'], conf['address']['port'])

    simulator._protocol = protocol()
    simulator._srv = await simulator._protocol.connect_cb(
        simulator._connection_cb,
        simulator._interrogate_cb,
        simulator._command_cb,
        address)

    simulator._connections = set()
    simulator._async_group = aio.Group()
    simulator._executor = aio.create_executor()

    await simulator._executor(pandapower.runpp, simulator.pp.net)

    print("state filled, run adapter now")
    simulator._async_group.spawn(simulator._main_loop)
    simulator.previous = set()

    await simulator._notify()
    await simulator.wait_closed()
