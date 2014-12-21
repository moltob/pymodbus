"""Asynchronous framework adapter for asyncio."""
import asyncio
from functools import partial
from pymodbus.client import async_common


class AsyncioAdapter(asyncio.Protocol):
    """Adapter of asynchronous functions to asyncio.

    Class is simply delegating between owner and asyncio. Callbacks of the
    framework are forwarded to owner and calls of owner are adapted to
    framework."""

    #: Object owning this adapter instance.
    owner = None

    #: Transport object of current connection.
    transport = None

    def connection_made(self, transport):
        self.transport = transport
        self.owner.connectionMade()

    def connection_lost(self, reason):
        self.transport = None
        self.owner.connectionLost(reason)

    def data_received(self, data):
        self.owner.dataReceived(data)

    def create_future(self):
        return asyncio.Future()

    def resolve_future(self, f, result):
        f.set_result(result)

    def raise_future(self, f, exc):
        f.set_exception(exc)

#---------------------------------------------------------------------------#
# Convenience definitions
#---------------------------------------------------------------------------#
ModbusClientProtocol = partial(async_common.ModbusClientProtocol, AsyncioAdapter())
