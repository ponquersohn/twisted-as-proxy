from twisted.web.proxy import ProxyClientFactory, ReverseProxyResource, ProxyClient

from ActiveSyncProxyClient import ActiveSyncProxyClient

class ActiveSyncProxyClientFactory(ProxyClientFactory):
    protocol = ActiveSyncProxyClient
    def __init__(self, *args, **kwargs):
        self.host = ''
        self.realhost = ''
        self.rp = None
        self.cache = None
        self.key = None
        ProxyClientFactory.__init__(self,*args,**kwargs)

    def buildProtocol(self, addr):
        print "Building protocol"
        p = self.protocol(self.command, self.rest, self.version,
                             self.headers, self.data, self.father)
        p.factory = self
        return p
