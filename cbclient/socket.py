
from autobahn.twisted.websocket import WebSocketClientProtocol, WebSocketClientFactory
from twisted.internet.protocol import ClientFactory, ReconnectingClientFactory
from twisted.python import log
from twisted.logger import Logger
log = Logger()

class CBClientProtocol(WebSocketClientProtocol):

    def onConnect(self, response):
        self.factory.resetDelay()
        self.factory.connections.append(self)
        self.handleConnect(response)

    def onOpen(self):
        self.handleOpen()

    def onMessage(self, message, isBinary):
        self.handleMessage(message, isBinary)

    def onClose(self, wasClean, code, reason):
        self.factory.connections.remove(self)
        self.handleClose(wasClean, code, reason)
        #self.socks.transport.loseConnection()


class CBSocketFactory(WebSocketClientFactory, ReconnectingClientFactory):

    connections = []
    '''
    def startedConnecting(self, connector):
        print 'Factory started to connect.'
    '''

    def sendMessage(self, data):
        for connection in self.connections:
            connection.sendMessage(data)

    def clientConnectionFailed(self, connector, reason):
        self.handleClientConnectionFailed(self, connector, reason)
        self.stopTrying()
        #self.retry(connector)

    def clientConnectionLost(self, connector, reason):
        print("Client connection lost .. retrying ..")
        print "reason is", reason
        #self.stopTrying()
        self.retry(connector)

