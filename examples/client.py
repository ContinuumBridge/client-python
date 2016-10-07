
from twisted.internet import reactor
# Import cbclient from the parent directory
import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
print("sys.path: %s", sys.path)
from cbclient import CBClient
import json

client = CBClient(key="f46653c385ak7DJh3G1Ema7dPZNV9IOCnmL1TBdgr83qr1Gx8AMcBWmL28ijDNe8"
                  , reactor=reactor)

def onMessage(response, isBinary):
    #print("Client message received: {0}".format(response.decode('utf8')))
    print("Client message received: " + str(json.loads(response)))

client.onMessage = onMessage

reactor.run()

