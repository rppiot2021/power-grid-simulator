from hat import aio
from hat import util
from hat.drivers import iec104
import urllib.parse
import logging

from simulator import common

mlog = logging.getLogger(__name__)


async def create(conf, points, simulation):
    slave = IEC104Slave()

    name = conf['name']
    iec104_to_key = {}
    key_to_iec104 = {}
    iec104_to_point = {}
    for point in points:
        output = util.first(point['outputs'], lambda o: o['name'] == name)
        if output is None:
            mlog.warning('104 slave named %s received point with no matching '
                         'output', name)
            continue
        iec104_id = (output['asdu'], output['io'])
        simulation_id = (point['table'], point['property'], point['id'])
        iec104_to_key[iec104_id] = simulation_id
        key_to_iec104[simulation_id] = iec104_id
        iec104_to_point[iec104_id] = point
    slave._iec104_to_key = iec104_to_key
    slave._key_to_iec104 = key_to_iec104
    slave._iec104_to_point = iec104_to_point

    slave._async_group = aio.Group()
    slave._connections = set()
    slave._simulation = simulation

    url = urllib.parse.urlparse(conf['address'])
    slave._server = await iec104.listen(
        connection_cb=slave._on_connection,
        addr=iec104.Address(url.hostname, url.port),
        interrogate_cb=slave._on_interrogate,
        command_cb=slave._on_command)

    simulation.subscribe_to_state_change(slave._on_state_change)
    return slave


class IEC104Slave(common.Server):

    @property
    def async_group(self):
        return self._async_group

    def _on_connection(self, connection):
        self._connections.add(connection)
        self._async_group.spawn(aio.call_on_done, connection.wait_closing(),
                                self._connections.remove, connection)

    def _on_interrogate(self, connection, requested_asdu):
        resu = [self._simulation_to_data(key,
                                         iec104.Cause.INTERROGATED_STATION)
                for (asdu, io), key in self._iec104_to_key.items()
                if asdu == requested_asdu or requested_asdu == 0xFFFF]
        return resu

    def _on_command(self, connection, commands):
        success = []
        for command in commands:
            if command.action != iec104.Action.EXECUTE:
                mlog.warning('only execute commands are supported, '
                             'ignoring %s', command)
                continue
            iec104_id = (command.asdu_address, command.io_address)
            key = self._iec104_to_key[iec104_id]
            point = self._iec104_to_point[iec104_id]

            if point['type'] == 'float':
                value = command.value
            elif point['type'] == 'single':
                value = command.value == iec104.SingleValue.ON
            else:
                raise ValueError

            self._simulation.modify_state(*key, value)
            success.append(True)
        return success

    def _on_state_change(self, keys):
        changes = [self._simulation_to_data(key, iec104.Cause.SPONTANEOUS)
                   for key in keys if key in self._key_to_iec104]
        for connection in self._connections:
            connection.notify_data_change(changes)

    def _simulation_to_data(self, key, cause):
        asdu, io = self._key_to_iec104[key]
        point = self._iec104_to_point[(asdu, io)]
        sim_value = self._simulation.get_state(*key)
        if point['type'] == 'float':
            value = iec104.FloatingValue(sim_value)
        elif point['type'] == 'single':
            value = (iec104.SingleValue.ON if sim_value
                     else iec104.SingleValue.OFF)
        else:
            raise ValueError
        return iec104.Data(value=value,
                           quality=iec104.Quality(False, False, False, False,
                                                  False),
                           time=None,
                           asdu_address=asdu,
                           io_address=io,
                           cause=cause,
                           is_test=False)
