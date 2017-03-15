import pprint
class SSLActiveSyncProxyRequest(Request):
    """
    Used by ReverseProxy to implement a simple reverse proxy.
    @ivar proxyClientFactoryClass: a proxy client factory class, used to create
        new connections.
    @type proxyClientFactoryClass: L{ClientFactory}
    @ivar reactor: the reactor used to create connections.
    @type reactor: object providing L{twisted.internet.interfaces.IReactorTCP}
    """
    def logDebug(self, funct, message):
        cname = "SSLActiveSyncProxyRequest";
        print ("{}:      {}.{}(): {}".format(self.uuid, cname, funct, message))

    proxyClientFactoryClass = ActiveSyncProxyClientFactory
    def __init__(self, channel, queued=_QUEUED_SENTINEL, reactor=reactor):
        self.logDebug("__init__", "Called")
        Request.__init__(self, channel, queued)
        self.reactor = reactor
    def process(self):
        self.logDebug("process", "Called")
        self.requestHeaders.setRawHeaders(b"host",
                                          [self.factory.host.encode('ascii')])
        pprint.pprint(self)
                                          
        #clientFactory = self.proxyClientFactoryClass(
        #    self.method, self.uri, self.clientproto, self.getAllHeaders(),
        #    self.content.read(), self)
        #self.reactor.connectSSL(self.factory.host, self.factory.port,
                            #    clientFactory)