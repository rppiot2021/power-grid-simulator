from hat import util
from hat import aio
from hat.drivers import modbus
from hat.drivers import tcp
import urllib.parse
import logging
import struct

from simulator import common

mlog = logging.getLogger()


async def create(conf, points, simulation):
    slave = ModbusServer()

    name = conf['name']
    modbus_to_key = {}
    key_to_modbus = {}
    modbus_to_point = {}
    for point in points:
        output = util.first(point['outputs'], lambda o: o['name'] == name)
        if output is None:
            mlog.warning('modbus slave named %s received point with no '
                         'matching output', name)
            continue
        modbus_id = (modbus.DataType[output['data_type']], output['address'])
        simulation_id = (point['table'], point['property'], point['id'])
        modbus_to_key[modbus_id] = simulation_id
        key_to_modbus[simulation_id] = modbus_id
        modbus_to_point[modbus_id] = point
    slave._modbus_to_key = modbus_to_key
    slave._key_to_modbus = key_to_modbus
    slave._modbus_to_point = modbus_to_point

    slave._async_group = aio.Group()
    slave._simulation = simulation

    url = urllib.parse.urlparse(conf['address'])
    slave._server = await modbus.create_tcp_server(
        modbus.ModbusType.TCP,
        tcp.Address(url.hostname, url.port),
        read_cb=slave._on_read,
        write_cb=slave._on_write)
    return slave


class ModbusServer(common.Server):

    @property
    def async_group(self):
        return self._async_group

    def _on_read(self, slave, device_id, data_type, start_address, quantity):
        results = []
        address = start_address
        while len(results) < quantity:
            address = start_address + len(results)

            modbus_id = data_type, address
            key = self._modbus_to_key.get(modbus_id)
            if key is None:
                results.append(0)
                continue
            point = self._modbus_to_point[modbus_id]
            simulation_value = self._simulation.get_state(*key)
            if point['type'] == 'single':
                values = [1 if simulation_value else 0]
            elif point['type'] == 'float':
                b = struct.pack('f', simulation_value)
                values = [int(b[0]), int(b[1]), int(b[2]), int(b[3])]
            else:
                raise ValueError
            results.extend(values)
        return results

    def _on_write(self, slave, device_id, data_type, start_address, values):
        for address, value in enumerate(values, start_address):
            modbus_id = data_type, address
            key = self._modbus_to_key.get(modbus_id)
            if key is None:
                mlog.warning('modbus interface not configured for writing '
                             'on %s address %s ignoring', data_type, address)
                continue
            point = self._modbus_to_point[modbus_id]
            if point['type'] == 'float':
                simulation_value = value
            if point['type'] == 'single':
                simulation_value = bool(value)
            else:
                raise ValueError

            self._simulation.modify_state(*key, simulation_value)
