from hat import aio
from hat import util
import abc
import typing


class Server(aio.Resource):
    """Interface that represents a protocol server/slave. Receives a reference
    to a simulation object, which it uses to access simulation state or affects
    it based on messages it receives from its clients."""


class Simulation(aio.Resource):
    """Interface that represents a simulation object. Contains the logic of the
    physical aspects of the simulation, while offering access to its state and
    methods for its modification. Physical elements are referenced with a
    three-part identifier - table (representing a pandapower table in which
    concrete value is stored), property (representing the column of the
    table) and identifier (representing the row)"""

    @abc.abstractmethod
    def subscribe_to_state_change(
            self,
            callback: typing.Callable[[typing.Tuple[str, str, int]], None]
    ) -> util.RegisterCallbackHandle:
        """Subscribes to any state change. When state changes, the callback
        is called with a list of identifiers that were affected."""

    @abc.abstractmethod
    def get_state(self, table: str, prop: str, identifier: int) -> typing.Any:
        """Returns the state of an element that was requested."""

    @abc.abstractmethod
    def modify_state(self,
                     table: str,
                     prop: str,
                     identifier: int,
                     value: typing.Any):
        """Requests the simulation to modify its state. Value selector
        arguments are equivalent to the ``get_state`` method, with addition of
        the last argument, which is a value to which the state will be set."""
