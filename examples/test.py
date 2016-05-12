
import json
import sys
from twisted.python import log
from twisted.internet import reactor
log.startLogging(sys.stdout)
from cbclient import CBClient

class MyClient(CBClient):

    def onConnect(self, response):
        print("MyClient Server connected: {0}".format(response.peer))
        self.factory.resetDelay()

    def onOpen(self):
        print("WebSocket connection open.")

        def hello():
            #self.sendMessage(u"Hello, world!".encode('utf8'))
            self.sendMessage("CID52", "Hey")
            #self.sendMessage(b"\x00\x01\x03\x04", isBinary=True)
            self.factory.reactor.callLater(1, hello)

        # start sending messages every second ..
        hello()

    def onMessage(self, message, isBinary):
        print "CBClientProtocol onMessage"
        #raise NotImplementedError(self)

    def onClose(self, wasClean, code, reason):
        print "CBClientProtocol onClose"
        #self.socks.transport.loseConnection()


client = MyClient(is_bridge=True, reactor=reactor)

reactor.run()
