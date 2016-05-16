
from twisted.internet import reactor
# Import cbclient from the parent directory
import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from cbclient import CBClient

client = CBClient(key=""
                  , reactor=reactor)

reactor.run()

