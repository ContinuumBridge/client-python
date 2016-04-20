
from twisted.internet import reactor
import time
from cbclient import CBProtocol, CBConnectionFactory

from cbclient import SocketThreadWrapper

key = "255a3f81gPVwTy2qHcRrJHQ+yLnYvEFdOvNq3cKGVXNa80WEVRzdbsyaf+RT7dJV"

f = CBConnectionFactory()
#f.protocol = CBProtocol
#s = CBConnection(f, key=key, is_bridge=True)

reactor.connectTCP("127.0.0.1", 9000, f)

reactor.run()

'''
wrapper = SocketThreadWrapper(key, is_bridge=True)
while True:
    pass

client = CBClientThread()
client.start()
client.cmd_q.put(CBClientCommand(CBClientCommand.SEND, {'test': 'testing'}))
time.sleep(600)
'''
