"""Asynchronous adapter implementation for Twisted."""
from functools import partial
from twisted.internet import defer, protocol
from twisted.python.failure import Failure
from pymodbus.client import async_common


class TwistedAdapter(protocol.Protocol):
    """Adapter of asynchronous functions to Twisted networking engine.

    Class is simply delegating between owner and Twisted. Callbacks of the
    framework are forwarded to owner and calls of owner are adapted to
    framework."""

    #: Object owning this adapter instance.
    owner = None

    def connectionMade(self):
        self.owner.connectionMade()

    def connectionLost(self, reason=protocol.connectionDone):
        self.owner.connectionLost(reason)

    def dataReceived(self, data):
        self.owner.dataReceived(data)

    def create_future(self):
        return defer.Deferred()

    def resolve_future(self, f, result):
        f.callback(result)

    def raise_future(self, f, exc):
        f.fail(Failure(exc))

#---------------------------------------------------------------------------#
# Convenience definitions
#---------------------------------------------------------------------------#
ModbusClientProtocol = partial(async_common.ModbusClientProtocol, TwistedAdapter())
