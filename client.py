
import json
import requests
import retrying
from socketIO_client import SocketIO, BaseNamespace
#from twisted.internet import protocol, reactor, endpoints

# Environment variables
CB_ADDRESS = "staging.continuumbridge.com"
KEY = "255a3f81gPVwTy2qHcRrJHQ+yLnYvEFdOvNq3cKGVXNa80WEVRzdbsyaf+RT7dJV"

# Constants
BRIDGE_AUTH_SUFFIX = "/api/bridge/v1/bridge_auth/login/"
BRIDGE_SOCKET_SUFFIX = "/sockets/bridge"
CLIENT_AUTH_SUFFIX = "/api/client/v1/client_auth/login/"
CLIENT_SOCKET_SUFFIX = "/sockets/client"

class CBNamespace(BaseNamespace):

    def on_connect(self):
        print "Connected"
        print('[Connected]')

    def on_message(self, *args):
        print ("Message: ", args)


class Client(object):

    connected = False

    def __init__(self, is_bridge=False):

        self.auth_url = "https://" + CB_ADDRESS \
                        + (BRIDGE_AUTH_SUFFIX if is_bridge else CLIENT_AUTH_SUFFIX)

    def connect(self):
        session_id = self.authorise()
        print "session_id  is", session_id
        self.create_socket(session_id)

    def authorise(self):

        print "self.auth_url is", self.auth_url
        auth_data = '{"key": "' + KEY + '"}'
        auth_headers = {'content-type': 'application/json'}
        response = requests.post(self.auth_url, data=auth_data, headers=auth_headers)
        print "response.text is", response.text
        self.cbid = json.loads(response.text)['cbid']
        return response.cookies['sessionid']

    def create_socket(self, session_id):

        self.socket = SocketIO('https://' + CB_ADDRESS + BRIDGE_SOCKET_SUFFIX, 443
                          , CBNamespace
                          , cookies={'sessionid': session_id})
                          #, verify=False)
        #self.socket.emit('message', {'test': 'test'})
        #self.socket.emit('message')
        print "Emitting message 1"
        self.socket.emit('message', {'test': 'test'})
        self.socket.wait(seconds=3)
        print "Emitting message 2"
        self.socket.emit('message', {'test': 'test'})


    '''
    def connect(self) :
        #auth_url = "https://" + CB_ADDRESS +

        ws_url = "ws://" + CB_ADDRESS + ":7522/"
        websocket.enableTrace(True)
        self._ws = websocket.WebSocketApp(
                        ws_url,
                        on_open   = self._onopen,
                        header = ['sessionID: {0}'.format(sessionID)],
                        on_message = self._onmessage)
        self._ws.run_forever()

    def _onopen(self, ws):
        print "on_open"

    def _onmessage(self, ws, message):
        print "on_message", message
        msg = json.loads(message)
        if msg['body'] == "connected":
            #ws.send('{"destination": "CID71", "source": "' + self.cbid + '", "body": "Hey client 71"}')
            ws.send('{"destination": "CID71", "source": "BID27/AID10", "body": "Hey client 71"}')
    '''

client = Client()
client.connect()