from PySide import QtCore
from twisted.internet.protocol import DatagramProtocol

from utils import get_log_handler
logger = get_log_handler(__name__)


class ClientEmitter(QtCore.QObject):
    """
    Helper to emit Signals in twisted class.
    Because the twisted class does not inherits from 'object', we can not
    use multiple inheritance mixing twisted's classes and PySide ones.
    """
    got_client = QtCore.Signal(str, int)
    got_data = QtCore.Signal(str)


class MulticastPingPong(DatagramProtocol):
    MULTICAST_ADDR = ('228.0.0.5', 8005)
    CMD_PING = "PING"
    CMD_PONG = "PONG"
    CMD_DATA = "DATA:"

    def __init__(self):
        self._client_emitter = ClientEmitter()

    def startProtocol(self):
        """
        Called after protocol has started listening.
        """
        # Set the TTL>1 so multicast will cross router hops:
        self.transport.setTTL(5)
        # Join a specific multicast group:
        self.transport.joinGroup(self.MULTICAST_ADDR[0])

    def send_alive(self):
        """
        Sends a multicast signal asking for clients.
        The receivers will reply if they want to be found.
        """
        self.transport.write(self.CMD_PING, self.MULTICAST_ADDR)

    def datagramReceived(self, datagram, address):
        logger.debug("Datagram %s received from %s" % (
            repr(datagram), repr(address)))

        if datagram.startswith(self.CMD_PING):
            # someone publishes itself, we reply that we are here
            self.transport.write(self.CMD_PONG, address)
        elif datagram.startswith(self.CMD_PONG):
            # someone reply to our publish message
            self.got_client.emit(address[0], address[1])
        elif datagram.startswith(self.CMD_DATA):
            # someone sent us a message
            data = datagram.lstrip(self.CMD_DATA)
            self.got_data.emit(data)

    def send_data(self, data, addr=None):
        """
        Helper to send data.
        If we do not supply an address, it will be send to everybody.
        """
        if addr is None:
            addr = self.MULTICAST_ADDR

        data = self.CMD_DATA + data
        self.transport.write(data, addr)

    @property
    def got_client(self):
        """
        Helper to forward the emitter's signal.
        """
        return self._client_emitter.got_client

    @property
    def got_data(self):
        """
        Helper to forward the emitter's signal.
        """
        return self._client_emitter.got_data


if __name__ == '__main__':
    # We use listenMultiple=True so that we can run multiple instances
    # on same machine.
    from twisted.internet import reactor

    reactor.listenMulticast(8005, MulticastPingPong(),
                            listenMultiple=True)
    reactor.run()
