from twisted.web.resource import Resource
from twisted.internet import reactor, ssl
from twisted.web.proxy import ProxyClientFactory, ReverseProxyResource, ProxyClient
from twisted.python.compat import urllib_parse, urlquote
from twisted.web.server import NOT_DONE_YET

from ActiveSyncProxyClientFactory import ActiveSyncProxyClientFactory

class SSLActiveSyncProxyResource(Resource):
    """
    Resource that renders the results gotten from another server
    Put this resource in the tree to cause everything below it to be relayed
    to a different server.
    @ivar proxyClientFactoryReverseClass: a proxy client factory class, used to create
        Reversenew connections.
    Reverse@type proxyClientFactoryClass: L{ClientFactory}
Reverse
    Reverse@ivar reactor: the reactor used to create connections.
    @type reactor: object providing L{twisted.internet.interfaces.IReactorTCP}
    """
    #proxyClientFactoryClass = ActiveSyncProxyClientFactory
    
    def logDebug(self, funct, message):
        print ("SSLActiveSyncProxyResource.{}(): {}".format(funct, message))
    def __init__(self, host, port, path, reactor=reactor, proxyClientFactoryClass=ActiveSyncProxyClientFactory):
        """
        @param host: the host of the web server to proxy.
        @type host: C{str}
        @param port: the port of the web server to proxy.
        @type port: C{port}
        @param path: the base path to fetch data from. Note that you shouldn't
            put any trailing slashes in it, it will be added automatically in
            request. For example, if you put B{/foo}, a request on B{/bar} will
            be proxied to B{/foo/bar}.  Any required encoding of special
            characters (such as " " or "/") should have been done already.
        @type path: C{str}
        """
        self.proxyClientFactoryClass = proxyClientFactoryClass
        Resource.__init__(self)
        self.host = host
        self.port = port
        self.path = path
        self.reactor = reactor
        
        
    def setProxyClientFactoryClass(self, proxyClientFactoryClass):
        self.proxyClientFactoryClass = proxyClientFactoryClass

    def getChild(self, path, request):
        """
        Create and return a proxy resource with the same proxy configuration
        as this one, except that its path also contains the segment given by
        C{path} at the end.
        """
        self.logDebug("getChild", "Requesting url: " + self.host + b'/' + urlquote(path, safe=b"").encode('utf-8'))
        return SSLActiveSyncProxyResource(
            self.host, self.port, self.path + b'/' + urlquote(path, safe=b"").encode('utf-8'),
            self.reactor)

    def render(self, request):
        """
        Render a request by forwarding it to the proxied server.
        """
        # RFC 2616 tells us that we can omit the port if it's the default port,
        # but we have to provide it otherwise
        self.logDebug("render" , "Called...")
        if self.port == 80:
            host = self.host
        else:
            host = self.host + u":" + str(self.port)
        request.requestHeaders.setRawHeaders(b"host", [host.encode('ascii')])
        request.content.seek(0, 0)
        qs = urllib_parse.urlparse(request.uri)[4]
        if qs:
            rest = self.path + b'?' + qs
        else:
            rest = self.path
        self.logDebug("render", "Creating factory")
        clientFactory = self.proxyClientFactoryClass(
            request.method, rest, request.clientproto,
            request.getAllHeaders(), request.content.read(), request)
        self.reactor.connectSSL(self.host, self.port, clientFactory, ssl.ClientContextFactory())
        self.logDebug("render", "NOT_DONE_YET")
        return NOT_DONE_YET
