
from twisted.internet import reactor
# Import cbclient from the parent directory
import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from cbclient import CBClient

class MyBridgeClient(CBClient):

    def onConnect(self, response):
        self.logger.info("MyBridgeClient Server connected: {0}".format(response.peer))

    def onOpen(self):
        self.logger.info("WebSocket connection open.")

        def hello():
            self.sendMessage("CID52", "Hey")
            #self.sendMessage(b"\x00\x01\x03\x04", isBinary=True)
            self.factory.reactor.callLater(10, hello)

        # start sending messages every second ..
        hello()

    def onMessage(self, message, isBinary):
        self.logger.info("Received message {0}".format(message))

    '''
    def onClose(self, wasClean, code, reason):
        print "CBClientProtocol onClose"
    '''


client = MyBridgeClient(key="",
                        is_bridge=True,
                        reactor=reactor)

reactor.run()
