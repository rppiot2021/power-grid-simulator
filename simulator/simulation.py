from hat import aio
from hat import util
import asyncio
import copy
import logging
import pandapower.networks
import random

from simulator import common

mlog = logging.getLogger(__name__)


_ref_net = pandapower.networks.example_simple()
pandapower.runpp(_ref_net)


async def create_simulation(conf):
    simulation = SimpleNetworkSimulation()

    simulation._points = conf['points']
    simulation._spontaneity = conf['spontaneity']
    simulation._net = copy.deepcopy(_ref_net)

    simulation._callback_registry = util.CallbackRegistry()
    simulation._async_group = aio.Group()
    simulation._async_group.spawn(simulation._main_loop)
    simulation._executor = aio.create_executor()

    await simulation._calculate()

    return simulation


class SimpleNetworkSimulation(common.Simulation):

    @property
    def async_group(self):
        return self._async_group

    def subscribe_to_state_change(self, callback):
        return self._callback_registry.register(callback)

    def get_state(self, table, prop, identifier):
        return _net_get_value(self._net, table, prop, identifier)

    def modify_state(self, table, prop, identifier, value):
        _net_set_value_exact(self._net, table, prop, identifier, value)
        self._callback_registry.notify([(table, prop, identifier)])
        self._async_group.spawn(self._calculate)

    async def _main_loop(self):
        while True:
            await asyncio.sleep(random.gauss(self._spontaneity['mu'],
                                             self._spontaneity['sigma']))

            index_pool = [index for index, _ in self._net['gen'].iterrows()]
            index = random.choice(index_pool)

            key = ('gen', 'p_mw', index)
            _net_set_value_random(self._net, *key)
            await self._calculate()

    async def _calculate(self):
        net_old = copy.deepcopy(self._net)
        await self._executor(_ext_calculate_flows, self._net)
        changes = []
        print('>' * 80)
        for point in self._points:
            key = (point['table'], point['property'], point['id'])
            current = _net_get_value(self._net, *key)
            previous = _net_get_value(net_old, *key)
            if current != previous:
                changes.append(key)
                print(f'{key} {previous:.2f} -> {current:.2f}')
        self._callback_registry.notify(changes)


def _net_get_value(net, table, column, index):
    return getattr(net, table)[column][index]


def _net_set_value_random(net, table, column, index):
    initial_value = _net_get_value(_ref_net, table, column, index)
    getattr(net, table)[column][index] = max(
        random.uniform(initial_value * 0.75, initial_value * 1.25), 0)


def _net_set_value_exact(net, table, column, index, value):
    series = getattr(net, table)[column]
    series[index] = value


def _ext_calculate_flows(net):
    pandapower.runpp(net)
