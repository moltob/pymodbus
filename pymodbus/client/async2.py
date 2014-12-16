"""
Implementation of a Modbus Client Using asyncio
-----------------------------------------------

Example run::

    import asyncio
    from pymodbus.client.async2 import ModbusClientProtocol


    @asyncio.coroutine
    def process():
        transport_, protocol_ = yield from asyncio.get_event_loop().create_connection(ModbusClientProtocol, "localhost", 502)

        result = yield from protocol_.read_coils(1)
        print("Result: %d" % result.bits[0])

        transport_.close()


    loop = asyncio.get_event_loop()
    loop.run_until_complete(process())
    loop.close()
"""
from pymodbus.factory import ClientDecoder
from pymodbus.exceptions import ConnectionException
from pymodbus.transaction import ModbusSocketFramer
from pymodbus.transaction import FifoTransactionManager
from pymodbus.transaction import DictTransactionManager
from pymodbus.client.common import ModbusClientMixin
from asyncio import Protocol, DatagramProtocol, Future

#---------------------------------------------------------------------------#
# Logging
#---------------------------------------------------------------------------#
import logging

_logger = logging.getLogger(__name__)


#---------------------------------------------------------------------------#
# Connected Client Protocols
#---------------------------------------------------------------------------#
class ModbusClientProtocol(Protocol, ModbusClientMixin):
    '''
    This represents the base modbus client protocol.  All the application
    layer code is deferred to a higher level wrapper.
    '''

    transport = None

    def __init__(self, framer=None):
        ''' Initializes the framer module

        :param framer: The framer to use for the protocol
        '''
        self._connected = False
        self.framer = framer or ModbusSocketFramer(ClientDecoder())
        if isinstance(self.framer, ModbusSocketFramer):
            self.transaction = DictTransactionManager(self)
        else:
            self.transaction = FifoTransactionManager(self)

    def connection_made(self, transport):
        ''' Called upon a successful client connection.
        '''
        _logger.debug("Client connected to modbus server")
        self.transport = transport
        self._connected = True

    def connection_lost(self, reason):
        ''' Called upon a client disconnect

        :param reason: The reason for the disconnect
        '''
        _logger.debug("Client disconnected from modbus server: %s" % reason)
        self._connected = False
        for tid in list(self.transaction):
            handler = self.transaction.getTransaction(tid)
            assert isinstance(handler, Future)
            handler.set_exception(ConnectionException('Connection lost during request'))

    def data_received(self, data):
        ''' Get response, check for valid message, decode result

        :param data: The data returned from the server
        '''
        self.framer.processIncomingPacket(data, self._handleResponse)

    def execute(self, request):
        ''' Starts the producer to send the next request to
        consumer.write(Frame(request))
        '''
        request.transaction_id = self.transaction.getNextTID()
        packet = self.framer.buildPacket(request)
        self.transport.write(packet)
        return self._buildResponse(request.transaction_id)

    def _handleResponse(self, reply):
        ''' Handle the processed response and link to correct deferred

        :param reply: The reply to process
        '''
        if reply is not None:
            tid = reply.transaction_id
            handler = self.transaction.getTransaction(tid)
            assert isinstance(handler, Future)
            if handler:
                handler.set_result(reply)
            else:
                _logger.debug("Unrequested message: " + str(reply))

    def _buildResponse(self, tid):
        ''' Helper method to return a deferred response
        for the current request.

        :param tid: The transaction identifier for this response
        :returns: A future linked to the latest request
        '''
        f = Future()
        if self._connected:
            self.transaction.addTransaction(f, tid)
        else:
            # mark future as immediately failed:
            f.set_exception(ConnectionException('Client is not connected'))
        return f


# Not yet ported:
# class ModbusUdpClientProtocol
# class ModbusClientFactory

# asyncio does not have a reconnecting client factory built-in, but even
# Twisted devs don't like the current approach, see:
# https://groups.google.com/forum/#!topic/python-tulip/9lIABK73zAc
#
# A similar approach was implemented at higher level in Tulip example
# code, see:
# https://github.com/leetreveil/tulip/blob/master/examples/cacheclt.py

#---------------------------------------------------------------------------#
# Exported symbols
#---------------------------------------------------------------------------#
__all__ = [
    "ModbusClientProtocol",
    # "ModbusUdpClientProtocol",
    # "ModbusClientFactory",
]
