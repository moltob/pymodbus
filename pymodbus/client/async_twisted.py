"""Asynchronous adapter implementation for Twisted."""
from twisted.internet import defer, protocol
from twisted.python.failure import Failure
from pymodbus.client.async_common import AsyncModbusClientMixin


class ModbusClientProtocol(protocol.Protocol, AsyncModbusClientMixin):
    """..."""

    def connectionMade(self):
        AsyncModbusClientMixin.connectionMade(self)

    def connectionLost(self, reason=protocol.connectionDone):
        AsyncModbusClientMixin.connectionLost(self, reason)

    def dataReceived(self, data):
        AsyncModbusClientMixin.dataReceived(self, data)

    def create_future(self):
        return defer.Deferred()

    def resolve_future(self, f, result):
        f.callback(result)

    def raise_future(self, f, exc):
        f.fail(Failure(exc))

    @property
    def transport_(self):
        return self.transport
