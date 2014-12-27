"""Asynchronous framework adapter for asyncio."""
import asyncio
from pymodbus.client.async_common import AsyncModbusClientMixin


class ModbusClientProtocol(asyncio.Protocol, AsyncModbusClientMixin):
    """Asyncio specific implementation of asynchronous modubus client protocol."""

    def connection_made(self, transport):
        self.transport = transport
        self._connectionMade()

    def connection_lost(self, reason):
        self.transport = None
        self._connectionLost(reason)

    def data_received(self, data):
        self._dataReceived(data)

    def create_future(self):
        return asyncio.Future()

    def resolve_future(self, f, result):
        f.set_result(result)

    def raise_future(self, f, exc):
        f.set_exception(exc)
