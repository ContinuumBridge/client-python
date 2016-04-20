
from socketIO_client import SocketIO, LoggingNamespace

import retrying
import Queue
from zope.interface import implementer
from twisted.web import proxy
from twisted.internet import reactor, protocol
from twisted.internet.protocol import ClientFactory, ReconnectingClientFactory
from twisted.internet.interfaces import ITransport, IFileDescriptor, IReadDescriptor
from twisted.python import log
import sys
log.startLogging(sys.stdout)

from .socket_io import SocketCommand, SocketReply
from .socket_wrapper import SocketThreadWrapper

#@implementer(IReadDescriptor, IFileDescriptor)
#@implementer(IReadDescriptor)
class CBProtocol(protocol.Protocol):

    authenticated = False
    connected = False

    def __init__(self, factory, key=None, is_bridge=False, address=None):

        print "CBConnection __init__"

        self.factory = factory
        self.address = address

        #self.socket_wrapper = SocketThreadWrapper(key=key, is_bridge=is_bridge, address=address)
        #self.factory.connections.add(self)
        #self.factory.reactor.addReader(self)
        self.doRead()

    def connectionMade(self):
        print "CBConnection connectionMade"
        '''
        peer = self.transport.getPeer()
        self.socks.makeReply(90, 0, port=peer.port, ip=peer.host)
        self.socks.otherConn=self
        '''

    def onMessage(self, message):
        print "CBConnection onMessage"
        """
        Called when message is received.
        Should be overridden to handle incoming messages.
        """
        #raise NotImplementedError(self)


    def connectionLost(self, reason):
        """
        Called when the connection is lost.
        """
        print "CBConnection connectionLost"
        #self.socks.transport.loseConnection()

    def dataReceived(self, message):
        print "CBConnection dataReceived"

        if message.type == SocketReply.MESSAGE:
            self.onMessage(message.data)
        if message.type == SocketReply.CONNECTED:
            self.connectionMade()
        elif message.type == SocketReply.DISCONNECTED:
            self.connectionLost()

    def doRead(self):
        print "CBConnection doRead"
        #message = self.socket_wrapper.do_read(self.onMessage)

    def write(self, data):
        print "CBConnection write", data

        self.socket_wrapper.send(data)
        '''
        self.socks.log(self, data)
        self.transport.write(data)
        '''

    def shutdown(self):

        print "CBConnection shutdown"
        self.factory.reactor.removeReader(self)

        self.factory.connections.discard(self)

        #self.socket.close()
        self.socket.cmd_q.put(SocketCommand(SocketCommand.CLOSE))
        self.socket = None

        self.factory = None


class CBConnectionFactory(ClientFactory):

    protocol = CBProtocol

    reactor = reactor

    def __init__(self):
        self.connections = set()

    def shutdown(self):
        """
        Shutdown factory.
        This is shutting down all created connections
        and terminating ZeroMQ context. Also cleans up
        Twisted reactor.
        """
        for connection in self.connections.copy():
            connection.shutdown()

        self.connections = None

    def buildProtocol(self, address):
        print "Factory buildProtocol", address
        return self.protocol()

    def startedConnecting(self, connector):
        print 'Factory started to connect.'

    def clientConnectionFailed(self, connector, reason):
        print 'Factory clientConnectionFailed', reason

    def clientConnectionLost(self, connector, reason):
        print 'Factory clientConnectionLost', reason

