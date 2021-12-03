from hat import aio
from hat import json
import asyncio
import click
import contextlib
import sys
from pathlib import Path

import simulator.protocols.iec104.slave
import simulator.protocols.modbus.server
import simulator.simulation

_package_path = Path(__file__).parent
_default_conf_path = _package_path / 'default_conf.yaml'


async def async_main(conf):
    group = aio.Group()

    simulation = await simulator.simulation.create_simulation(conf['process'])
    _bind_resource(simulation, group)

    for server_conf in conf['communication']:
        points_conf = [point for point in conf['process']['points']
                       if server_conf['name'] in
                       {output['name'] for output in point['outputs']}]
        fn = {
            'iec104': simulator.protocols.iec104.slave.create,
            'modbus': simulator.protocols.modbus.server.create,
        }[server_conf['type']]

        server = await aio.call(fn, server_conf, points_conf, simulation)
        _bind_resource(server, group)

    try:
        await group.wait_closing()
    finally:
        await aio.uncancellable(group.async_close())


def _bind_resource(resource, group):
    resource.async_group.spawn(aio.call_on_cancel, group.close)
    resource.async_group.spawn(aio.call_on_done, resource.wait_closing(),
                               group.close)
    group.spawn(aio.call_on_cancel, resource.close)
    group.spawn(resource.wait_closed)


@click.command()
@click.option('--conf-path', type=Path, default=_default_conf_path)
def main(conf_path):
    repo = json.SchemaRepository(_package_path / 'schema.yaml')
    conf = json.decode_file(conf_path)
    repo.validate('power-grid-simulator://schema.yaml#', conf)
    aio.init_asyncio()
    with contextlib.suppress(asyncio.CancelledError):
        aio.run_asyncio(async_main(conf))


if __name__ == '__main__':
    sys.exit(main())
