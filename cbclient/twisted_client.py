
from socketIO_client import SocketIO, LoggingNamespace

import retrying
import Queue
from zope.interface import implementer
from twisted.web import proxy
from twisted.internet import reactor
from twisted.internet import protocol
from twisted.internet.protocol import ClientFactory, ReconnectingClientFactory
from twisted.internet.interfaces import IFileDescriptor, IReadDescriptor
from twisted.python import log
import sys
log.startLogging(sys.stdout)

#from .socket_io import SocketThread, SocketCommand, SocketReply
from .socket_wrapper import SocketThreadWrapper

@implementer(IReadDescriptor, IFileDescriptor)
class CBConnection(object):

    authenticated = False
    connected = False

    def __init__(self, factory, address=None):

        print "CBConnection __init__"

        self.factory = factory
        self.address = address

        self.socket_wrapper = SocketThreadWrapper(is_bridge=True)
        #self.socket.on('message', self.onMessage)
        #self.socks=socks
        self.factory.connections.add(self)

        self.factory.reactor.addReader(self)
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
        print "CBConnection connectionLost"
        self.socks.transport.loseConnection()

    def dataReceived(self,data):
        print "CBConnection dataReceived"
        self.socks.write(data)

    def doRead(self):

        print "doRead"

        try:
            reply = self.socket.reply_q.get(block=False)

            if reply.type == SocketReply.MESSAGE:
                log.callWithLogger(self, self.messageReceived, reply.data)

            elif reply.type == SocketReply.CONNECTED:
                print "Client received CONNECTED"

            elif reply.type == SocketReply.DISCONNECTED:
                print "Client received DISCONNECTED"

        except Queue.Empty:
            pass



    def write(self, data):
        print "CBConnection write", data
        self.socks.log(self,data)
        self.transport.write(data)

    def shutdown(self):

        print "CBConnection shutdown"
        self.factory.reactor.removeReader(self)

        self.factory.connections.discard(self)

        #self.socket.close()
        self.socket.cmd_q.put(SocketCommand(SocketCommand.CLOSE))
        self.socket = None

        self.factory = None


class CBConnectionFactory(ClientFactory):

    protocol = CBConnection

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
        print 'Factory clientConnectionFailed'

    def clientConnectionLost(self, connector, reason):
        print 'Factory clientConnectionLost'

