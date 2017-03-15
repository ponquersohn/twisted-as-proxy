
class SSLActiveSyncProxy(HTTPChannel):
    """
    Implements a simple reverse proxy.
    For details of usage, see the file examples/reverse-proxy.py.
    """
    requestFactory = SSLActiveSyncProxyRequest
    
    def logDebug(self, funct, message):
        print ("SSLActiveSyncProxyResource.{}(): {}".format(funct, message))

    def __init__(self, *args, **kwargs):
        self.logDebug("__init__", "Called")
        HTTPChannel(self, *args, **kwargs)
