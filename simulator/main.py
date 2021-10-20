from pathlib import Path
import click
import sys
from hat import aio
from hat import json
from simulator_connection import ConnectionIEC104
from simulator import run_sim
default_conf_path = 'conf.yaml'


def notify(output):
    print("NOTIFY  ", len(output))
def new_value(output):
    print(output, end="")

@click.command()
@click.option('--conf-path', type=Path, default=default_conf_path)
def main(conf_path):
    conf = json.decode_file(conf_path)
    aio.init_asyncio()
    aio.run_asyncio(run_sim(conf, ConnectionIEC104, notify, new_value))


if __name__ == '__main__':
    print("simulator started")
    sys.exit(main())
