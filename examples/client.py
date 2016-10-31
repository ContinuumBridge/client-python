
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
            self.factory.reactor.callLater(10, hello)

        # start sending messages every ten seconds ..
        hello()


client = MyClient(key="",
                  is_bridge=False,
                  reactor=reactor)

reactor.run()

