
from twisted.internet import reactor
# Import cbclient from the parent directory
import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from cbclient import CBClient
import json

class MyBridgeClient(CBClient):

    def onConnect(self, response):
        self.logger.info("MyBridgeClient Server connected: {0}".format(response.peer))
        self.factory.resetDelay()

    def onOpen(self):
        self.logger.info("WebSocket connection open.")

        def hello():
            destination = "cb",
            body = {
                "verb": "patch",
                "resource": "/api/bridge/v1/bridge/106/",
                "body": {
                "status": "starting"
                }
            }
            client.sendMessage(destination, body)
            #client.sendMessage("CID52", {"key": "value"})
            self.factory.reactor.callLater(10, hello2)

        def hello2():
            destination = "cb",
            body = {
                "verb": "patch",
                "resource": "/api/bridge/v1/bridge/106/",
                "body": {
                "status": "running"
                }
            }
            client.sendMessage(destination, body)
            #client.sendMessage("CID52", {"key": "value"})
            self.factory.reactor.callLater(10, hello)
        
        # start sending messages every second ..
        hello()

    def onMessage(self, message, isBinary):
        self.logger.info("onMessage: " + str(message))
        self.logger.info("")

    '''
    def onClose(self, wasClean, code, reason):
        print "CBClientProtocol onClose"
    '''

def goForIt():
    destination = "cb",
    body = {
        "verb": "patch",
        "resource": "/api/bridge/v1/bridge/106/",
        "body": {
        "status": "running"
        }
    }
    client.sendMessage(destination, body)
    #client.sendMessage("CID52", {"key": "value"})
    reactor.callLater(4, goForIt)

client = MyBridgeClient(is_bridge=True, reactor=reactor)
#reactor.callLater(10, goForIt)

reactor.run()
