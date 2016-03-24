
from twisted.internet import reactor
# Import cbclient from the parent directory
import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from cbclient import CBClient

class MyClient(CBClient):

    def onConnect(self, response):
        self.logger.info("MyClient Server connected: {0}".format(response.peer))

    def onOpen(self):
        self.logger.info("WebSocket connection open.")

        def hello():
            self.sendMessage("BID2", "Hey")
            #self.sendMessage(b"\x00\x01\x03\x04", isBinary=True)
            self.factory.reactor.callLater(30, hello)

        # start sending messages every second ..
        hello()


client = MyClient(key=""
                  , reactor=reactor)

reactor.run()

