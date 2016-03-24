
from twisted.internet import reactor
import time
from cbclient import CBConnection, CBConnectionFactory

'''
client = CBClientThread()
client.start()
client.cmd_q.put(CBClientCommand(CBClientCommand.SEND, {'test': 'testing'}))
time.sleep(600)
'''

f = CBConnectionFactory()
s = CBConnection(f)

reactor.run()