import Queue
from twisted.internet import reactor, defer
from .socket_io import SocketThread, SocketCommand, SocketReply

class SocketThreadWrapper(object):

    unused_ids = []
    highest_id = 0
    deferred_requests = {}

    def __init__(self, *args, **kwargs):
        self.socket = SocketThread(*args, **kwargs)
        self.socket.start()

    def get_unused_id(self):
        try:
            return self.unused_ids.pop()
        except IndexError:
            self.highest_id += 1
            return self.highest_id

    def return_id(self, id):
        # This id is no longer in use, make it available for use
        self.unused_ids.append(id)

    def send(self, data):
        request = self.create_request(SocketCommand.SEND, data)
        self.socket.cmd_q.put(request)

    def create_request(self, type, data):
        deferred = defer.Deferred()
        self.deferred_requests[self.get_unused_id()] = deferred

    def do_read(self, dataReceived):
        print "SocketWrapper do_read"
        try:
            reply = self.socket.reply_q.get(block=False)
            dataReceived(reply)
            '''
            if reply.type == SocketReply.MESSAGE:
                print "SocketWrapper got message", reply.data
                #log.callWithLogger(self, self.messageReceived, reply.data)

            elif reply.type == SocketReply.CONNECTED:
                print "Client received CONNECTED"

            elif reply.type == SocketReply.DISCONNECTED:
                print "Client received DISCONNECTED"
            '''
        except Queue.Empty:
            pass

    def close(self):
        pass

    def handle_reply(self, reply):

        print "handle_reply reply", reply

        try:
            deferred = self.deferred_requests[reply.id]
            deferred.callback(reply.type, reply.data)
            self.return_id(reply.id)

        except KeyError:
            # The the reply id is unknown
            pass
        except AttributeError:
            # The reply has no id
            pass







