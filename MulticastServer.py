from PySide import QtCore
from twisted.internet.protocol import DatagramProtocol

from utils import get_log_handler
logger = get_log_handler(__name__)

MULTICAST_ADDR = ('228.0.0.5', 8005)
CMD_PING = "PING"
CMD_PONG = "PONG"
CMD_MSG = "MSG:"


class ClientEmitter(QtCore.QObject):
    """
    Helper to emit Signals in twisted class.
    Because the twisted class does not inherits from 'object', we can not
    use multiple inheritance mixing twisted's classes and PySide ones.
    """
    got_client = QtCore.Signal(str, int)
    got_message = QtCore.Signal(str)


class MulticastPingPong(DatagramProtocol):
    def __init__(self):
        self._client_emitter = ClientEmitter()

    def startProtocol(self):
        """
        Called after protocol has started listening.
        """
        # Set the TTL>1 so multicast will cross router hops:
        self.transport.setTTL(5)
        # Join a specific multicast group:
        self.transport.joinGroup(MULTICAST_ADDR[0])

        self.send_alive()

    def send_alive(self):
        """
        Sends a multicast signal asking for clients.
        The receivers will reply if they want to be found.
        """
        self.transport.write(CMD_PING, MULTICAST_ADDR)

    def datagramReceived(self, datagram, address):
        logger.debug("Datagram %s received from %s" % (
            repr(datagram), repr(address)))

        if datagram.startswith(CMD_PING):
            # someone publishes itself, we reply that we are here
            self.transport.write(CMD_PONG, address)
        elif datagram.startswith(CMD_PONG):
            # someone reply to our publish message
            self.got_client.emit(address[0], address[1])
        elif datagram.startswith(CMD_MSG):
            # someone sent us a message
            msg = datagram.lstrip(CMD_MSG)
            self.got_message.emit(msg)

    def send_message(self, message, addr=None):
        """
        Helper to send a message.
        If we do not supply an address, it will be send to everybody.
        """
        if addr is None:
            addr = MULTICAST_ADDR

        message = CMD_MSG + message
        self.transport.write(message, addr)

    @property
    def got_client(self):
        return self._client_emitter.got_client

    @property
    def got_message(self):
        return self._client_emitter.got_message


if __name__ == '__main__':
    # We use listenMultiple=True so that we can run MulticastServer.py and
    # MulticastClient.py on same machine:
    from twisted.internet import reactor

    reactor.listenMulticast(8005, MulticastPingPong(),
                            listenMultiple=True)
    reactor.run()
