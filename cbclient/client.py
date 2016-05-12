
from cookielib import CookieJar
import json
from math import ceil
import random
from twisted.internet import ssl
from twisted.internet.defer import Deferred
from twisted.internet.protocol import Protocol, ClientFactory, ReconnectingClientFactory
from twisted.web.client import Agent, CookieAgent
from twisted.web.http_headers import Headers
from twisted.web.iweb import IBodyProducer

from twisted.internet import reactor, defer
from twisted.logger import Logger
log = Logger()
#log.startLogging(sys.stdout)

from zope.interface import implements

from .conf import CB_ADDRESS, KEY, AUTH_PORT, AUTH_PROTOCOL, SOCKET_PORT, SOCKET_PROTOCOL, BRIDGE_AUTH_SUFFIX \
    , BRIDGE_SOCKET_SUFFIX, CLIENT_AUTH_SUFFIX, CLIENT_SOCKET_SUFFIX
from .socket import CBSocketFactory, CBClientProtocol

class StringProducer(object):
    implements(IBodyProducer)

    def __init__(self, body):
        self.body = body
        self.length = len(body)

    def startProducing(self, consumer):
        consumer.write(self.body)
        return defer.succeed(None)

    def pauseProducing(self):
        pass

    def stopProducing(self):
        pass

class BodyPrinter(Protocol):
    def __init__(self, finished):
        self.finished = finished
        self.remaining = 1024 * 10
        self.total_response = ""

    def dataReceived(self, bytes):
        if self.remaining:
            display = bytes[:self.remaining]
            self.total_response += display  # Append to our response.
            self.remaining -= len(display)

    def connectionLost(self, reason):
        # Finished receiving body
        self.finished.callback(self.total_response)

class CBClient(object):

    reactor = None

    factory = None

    connector = None

    auth_retry_num = 0

    auth_max_retries = -1

    auth_max_backoff = 300

    socket_backoff_factor = 2

    socket_max_backoff = 100

    def __init__(self, address=None, is_bridge=False, key=None, reactor=reactor):
        #self.connections = set()

        self.reactor = reactor
        self.auth_url = AUTH_PROTOCOL + "://" + CB_ADDRESS + ":" + str(AUTH_PORT) \
                            + (BRIDGE_AUTH_SUFFIX if is_bridge else CLIENT_AUTH_SUFFIX)
        self.auth_key = key if key else KEY
        self.socket_address = CB_ADDRESS
        self.socket_address_suffix = BRIDGE_SOCKET_SUFFIX if is_bridge else CLIENT_SOCKET_SUFFIX
        self.socket_port = SOCKET_PORT
        self.session_id = ""

        self.authenticate()

    def onConnect(self, response):
        # Override this
        log.info("CBClient Connected to {0}".format(response.peer))
        pass

    def _onConnect(self, response):
        self.onConnect(response)

    def onOpen(self):
        # Override this
        log.info("CB Client open")

    def _onOpen(self):
        self.onOpen()

    def onMessage(self, response, isBinary):
        print "response is", response
        print "response.decode('utf8') is", response.decode('utf8')

        log.info("CB Client message received: ")
        message = "CB Client message received: {0}".format(response.decode('utf8'))
        #m = 'CB Client message received: {"source":"cb","body":"connected"}'
        #m = 'CB Client message received: "source":"cb","body":"connected"'
        log.info(m)
        # Override this
        if isBinary:
            log.info("CB Client binary message received: {0} bytes".format(len(response)))
        else:
            pass
            #log.info(u"CB Client message received: " + response.decode('utf8'))
            #log.info("CB Client message received: {0}".format(response.decode('utf8')))

    def _onMessage(self, response, isBinary):
        self.onMessage(response, isBinary)

    def onClose(self, wasClean, code, reason):
        # Override this
        log.info("CB Client closed. Reason: {0}".format(reason))

    def _onClose(self, wasClean, code, reason):
        self.onClose(wasClean, code, reason)

    def authenticate(self):
        #self.session_id = cb_authenticate(self.auth_url)
        log.info("Authenticating")
        #print "self.auth_url is", self.auth_url
        cookieJar = CookieJar()
        agent = CookieAgent(Agent(self.reactor), cookieJar)
        data = '{"key": "' + self.auth_key + '"}'
        print "self.auth_url is", self.auth_url
        d = agent.request(
            'POST',
            self.auth_url,
            Headers({'User-Agent': ['Twisted Web Client Example'],
                     'content-type': ['application/json']}),
            StringProducer(data))
        d.addCallback(self.handleAuthResponse, cookieJar)
        d.addErrback(self.handleAuthFailed)

    def handleAuthFailed(self, reason):
        log.warn("Authentication failed. Reason: {0}".format(reason))
        self.reauthenticate()

    def handleAuthResponse(self, response, cookieJar):
        print "handle_auth_response response", response
        finished = Deferred()
        if response:
            response.deliverBody(BodyPrinter(finished))
            finished.addCallback(self.handleAuthResponseBody, cookieJar)
        else:
            log.warn("No response to authentication request")
            self.reauthenticate()

    def handleAuthResponseBody(self, bodyJSON, cookieJar):

        try:
            body = json.loads(bodyJSON)
        except ValueError, e:
            log.error("Could not parse auth response. Reason: {0}".format(e))
            return self.reauthenticate()

        for cookie in cookieJar:
            if cookie.name == "sessionid":
                self.session_id = cookie.value
                print "sessionid", cookie.value
        if self.session_id:
            self.auth_retry_num = 0
            self.cbid = body.get('cbid', '')
            print "self.cbid is", self.cbid
            self.setupSocket()
        else:
            log.warn("No session id in authentication response")
            self.reauthenticate()

    def reauthenticate(self):

        exp_backoff = pow(self.auth_retry_num, 2)
        backoff = min(ceil(exp_backoff * random.random()), self.auth_max_backoff)
        log.info("Trying again in {0} seconds.".format(int(backoff)))
        self.auth_retry_num += 1
        self.reactor.callLater(backoff, self.authenticate)

    def setupSocket(self):

        headers = {'sessionid': self.session_id}

        socket_url = u"{0}://{1}{2}".format(SOCKET_PROTOCOL, self.socket_address
                                                , self.socket_address_suffix)

        factory = self.factory = CBSocketFactory(socket_url, headers=headers)
        factory.handleClientConnectionFailed = self.handleClientConnectionFailed
        factory.handleClientConnectionLost = self.handleClientConnectionLost

        factory.protocol = protocol = CBClientProtocol
        protocol.handleMessage = self._onMessage
        protocol.handleOpen = self._onOpen
        protocol.handleConnect = self._onConnect
        protocol.handleClose = self._onClose

        if AUTH_PROTOCOL == "https":
            log.debug("Connecting ssl")
            contextFactory = ssl.ClientContextFactory()
            self.connector = self.reactor.connectSSL(self.socket_address, self.socket_port, self.factory, contextFactory)
        else:
            self.connector = self.reactor.connectTCP(self.socket_address, self.socket_port, self.factory)

    def sendMessage(self, destination, body):

        message = {
            'destination': destination,
            'source': self.cbid,
            'body': body
        }

        reactor.callFromThread(self.factory.sendMessage, json.dumps(message).encode('utf8'))

    def handleClientConnectionFailed(self, factory, connector, reason):
        log.info("Client socket connection failed. Reason: {0}".format(reason))
        self.destroySocket()
        self.reauthenticate()

    def handleClientConnectionLost(self, factory, connector, reason):
        log.info("Client socket connection lost. Reason: {0}".format(reason))
        factory.retry(connector)

    def destroySocket(self):

        self.factory.stopTrying()

        if self.connector:
            self.connector.disconnect()
            self.connector = None

