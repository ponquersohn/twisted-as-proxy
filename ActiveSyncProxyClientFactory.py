from twisted.web.proxy import ProxyClientFactory, ReverseProxyResource, ProxyClient
from ActiveSyncProxyClient import ActiveSyncProxyClient

class ActiveSyncProxyClientFactory(ProxyClientFactory):
    protocol = ActiveSyncProxyClient
    
    def logDebug(self, funct, message):
        cname = "ActiveSyncProxyClientFactory";
        print ("{}:      {}.{}(): {}".format(self.uuid, cname, funct, message))
        
    def __init__(self, uuid="NotDefinedYet", *args, **kwargs):
        self.uuid = uuid;
        self.logDebug("__init__", "Called")
        self.host = ''
        self.realhost = ''
        self.rp = None
        self.cache = None
        self.key = None
        ProxyClientFactory.__init__(self,*args,**kwargs)

    def buildProtocol(self, addr):
        self.logDebug("buildProtocol", "Called")
        p = self.protocol(self.uuid, self.command, self.rest, self.version,
                             self.headers, self.data, self.father)
        p.factory = self
        self.logDebug("buildProtocol", "Finished")
        return p
