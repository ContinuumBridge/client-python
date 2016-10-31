
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
            # If source kwarg is omitted the source is set to this BID
            self.sendMessage("CID17/AID58", {
                "body": [],
            }, source="BID3/AID57")
            self.factory.reactor.callLater(10, hello)

        # start sending messages every ten seconds ..
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
