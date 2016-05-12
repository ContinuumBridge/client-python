
import sys
from twisted.python import log
from twisted.internet import reactor
log.startLogging(sys.stdout)
from cbclient import CBClient

client = CBClient(is_bridge=False
                  , key="f46653c385ak7DJh3G1Ema7dPZNV9IOCnmL1TBdgr83qr1Gx8AMcBWmL28ijDNe8"
                  , reactor=reactor)

reactor.run()

