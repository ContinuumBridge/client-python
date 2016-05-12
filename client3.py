
import httplib
import json
import requests
import websocket

CB_ADDRESS = "127.0.0.1"
#CB_ADDRESS = "staging.continuumbridge.com"
KEY = ""

class Connection(object):
    def connect(self) :
        '''
        auth_url = "http://" + CB_ADDRESS + "/api/client/v1/client_auth/login/"
        auth_data = '{"key": "' + KEY + '"}'
        auth_headers = {'content-type': 'application/json'}
        response = requests.post(auth_url, data=auth_data, headers=auth_headers)
        self.cbid = json.loads(response.text)['cbid']
        '''
        #sessionID = response.cookies['sessionid']
        sessionID = "qkd323g7lj6jy8npq71jhum0ze1v6e7v"

        #ws_url = "ws://" + CB_ADDRESS + ":7522/"
        ws_url = "ws://" + CB_ADDRESS + ":9417/"
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
            ws.send('{"destination": "BID2", "source": "' + self.cbid + '", "body": "Hey bridge"}')

connection = Connection()
connection.connect()