"""Asynchronous framework adapter for asyncio."""
import asyncio
from pymodbus.client.async_common import AsyncModbusClientMixin


class ModbusClientProtocol(asyncio.Protocol, AsyncModbusClientMixin):
    """..."""

    #: Transport object of current connection.
    transport = None

    def connection_made(self, transport):
        self.transport = transport
        AsyncModbusClientMixin.connectionMade(self)

    def connection_lost(self, reason):
        self.transport = None
        AsyncModbusClientMixin.connectionLost(self, reason)

    def data_received(self, data):
        AsyncModbusClientMixin.dataReceived(self, data)

    def create_future(self):
        return asyncio.Future()

    def resolve_future(self, f, result):
        f.set_result(result)

    def raise_future(self, f, exc):
        f.set_exception(exc)

    @property
    def transport_(self):
        return self.transport
