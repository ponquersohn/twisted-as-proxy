
class SSLActiveSyncProxy(HTTPChannel):
    """
    Implements a simple reverse proxy.
    For details of usage, see the file examples/reverse-proxy.py.
    """
    requestFactory = SSLActiveSyncProxyRequest
