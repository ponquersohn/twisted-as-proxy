#!/usr/bin/python
from __future__ import absolute_import, division
from pprint import pprint
from twisted.python.compat import urllib_parse, urlquote
from twisted.internet import reactor, ssl
from twisted.internet.protocol import ClientFactory
from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET
from twisted.web.http import HTTPClient, Request, HTTPChannel, _QUEUED_SENTINEL
from twisted.web import proxy, server
from twisted.web.proxy import ProxyClientFactory, ReverseProxyResource, ProxyClient
from twisted.protocols.basic import LineReceiver
import base64, urlparse, StringIO, uuid, sys
import wbxml
import subprocess
import icapclient
import uuid


import xmltodict

icap_server = "192.168.127.10"
icap_method = "RESPMOD"

#from dewbxml import wbxmlparser, wbxmlreader, wbxmldocument, wbxmlelement, wbxmlstring
def pnqwbxml2xml(sourcexml):
    cmd  = ['/usr/local/bin/wbxml2xml', '-', '-l', 'ACTIVESYNC', '-o', '-' ]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          stdin=subprocess.PIPE)
    out, err = p.communicate(sourcexml)
    #print "err: %s" % err
    #print "out: %s" % out
    return out
#class DataReader(wbxmlreader):
#        def __init__(self, data):
#                self._wbxmlreader__bytes = StringIO.StringIO(data)

class ReverseProxyClient(ProxyClient):
    def __init__(self, *args, **kwargs):
        self.uuid = str(uuid.uuid1())
        self.resplength=0
        self._mybuffer = []
        self.encoding = ''
        self.ctype = ''
        self.headers_to_cache = {}
        self.commands = dict()
        ProxyClient.__init__(self,*args,**kwargs)
        print (self.uuid + " args:")
        pprint(self.father.args) 

    def handleHeader(self, key, value):
        print ("uuid: %s header: %s key: %s" % (self.uuid, key, value))
        if key == "Content-Type":
            self.replace = True
            self.ctype = value
        if key == "Content-Encoding":
            self.encoding = value
        self.headers_to_cache[key] = value
        
        ProxyClient.handleHeader(self, key, value)

    def handleResponsePart(self, buffer):
        print ("uuid: %s handleResponsePart buflen: %d" %(self.uuid, len(buffer)))
        self._mybuffer.append(buffer)
        self.resplength+=len(buffer)
        return NOT_DONE_YET

    def handleResponseEnd(self):
        if self._mybuffer is not None:
            b = ''.join(self._mybuffer)

        print ("uuid: %s handleResponseEnd resplength: %d b_length: %d" %(self.uuid, self.resplength, len(b)))
        if self.ctype == 'application/vnd.ms-sync.wbxml' and self.father.args.has_key('Cmd') and len(b)>0 :
            print "Found Content-Type: %s" % self.ctype
            print "Processing command: %s" % self.father.args['Cmd'][0]
            cmd = self.father.args['Cmd'][0]
            #xml = wbxml.wbxml_to_xml(b)

            if cmd in self.commands:
                self.commands[cmd]=self.commands[cmd]+1
            else:
                self.commands[cmd]=1
            f = open("oper/" + cmd + "." + str(self.commands[cmd]) + '.wbxml', "w")
            f.write(b)
            f.close()


            xml = pnqwbxml2xml(b)

            f = open("oper/" + cmd + "." + str(self.commands[cmd]) + '.xml', "w")
            f.write(xml)
            f.close()

            doc = xmltodict.parse(xml)
            f = open("oper/" + cmd + "." + str(self.commands[cmd]) + '.dict', "w")
            pprint(doc, f)
            f.close()

        
        if len(b) > 0:
            for buff in self._mybuffer:
                ProxyClient.handleResponsePart(self,buff)
            ProxyClient.handleResponsePart(self,"")    
        else:
            ProxyClient.handleResponsePart(self,b)
        #ProxyClient.handleResponsePart(self,b)
        print ("uuid: %s handleResponseEnd resplength: %d b_length: %d" %(self.uuid, self.resplength, len(b)))
        print ("uuid: %s handleResponseEndhandleResponseEnd: Finished" % (self.uuid))
        self.__buffer = None
    #ProxyClient.handleResponseEnd()
        #self.handleResponseEnd(self)
        return NOT_DONE_YET

class ReverseProxyClientFactory(ProxyClientFactory):
    protocol = ReverseProxyClient
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

class SSLReverseProxyRequest(Request):
    """
    Used by ReverseProxy to implement a simple reverse proxy.
    @ivar proxyClientFactoryClass: a proxy client factory class, used to create
        new connections.
    @type proxyClientFactoryClass: L{ClientFactory}
    @ivar reactor: the reactor used to create connections.
    @type reactor: object providing L{twisted.internet.interfaces.IReactorTCP}
    """
    proxyClientFactoryClass = ReverseProxyClientFactory
    def __init__(self, channel, queued=_QUEUED_SENTINEL, reactor=reactor):
        Request.__init__(self, channel, queued)
        self.reactor = reactor
    def process(self):
        self.requestHeaders.setRawHeaders(b"host",
                                          [self.factory.host.encode('ascii')])
        #clientFactory = self.proxyClientFactoryClass(
        #    self.method, self.uri, self.clientproto, self.getAllHeaders(),
        #    self.content.read(), self)
        #self.reactor.connectSSL(self.factory.host, self.factory.port,
                            #    clientFactory)
class SSLReverseProxy(HTTPChannel):
    """
    Implements a simple reverse proxy.
    For details of usage, see the file examples/reverse-proxy.py.
    """
    requestFactory = SSLReverseProxyRequest

class SSLReverseProxyResource(Resource):
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
    proxyClientFactoryClass = ReverseProxyClientFactory
    def __init__(self, host, port, path, reactor=reactor):
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
        Resource.__init__(self)
        self.host = host
        self.port = port
        self.path = path
        self.reactor = reactor

    def getChild(self, path, request):
        """
        Create and return a proxy resource with the same proxy configuration
        as this one, except that its path also contains the segment given by
        C{path} at the end.
        """
        print "Requesting url: " + self.host + b'/' + urlquote(path, safe=b"").encode('utf-8')
        return SSLReverseProxyResource(
            self.host, self.port, self.path + b'/' + urlquote(path, safe=b"").encode('utf-8'),
            self.reactor)

    def render(self, request):
        """
        Render a request by forwarding it to the proxied server.
        """
        # RFC 2616 tells us that we can omit the port if it's the default port,
        # but we have to provide it otherwise
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
        print "Creating factory"
        clientFactory = self.proxyClientFactoryClass(
            request.method, rest, request.clientproto,
            request.getAllHeaders(), request.content.read(), request)
        self.reactor.connectSSL(self.host, self.port, clientFactory, ssl.ClientContextFactory())
        return NOT_DONE_YET


site = server.Site(SSLReverseProxyResource('outlook.office365.com', 443, ''))
reactor.listenTCP(8081, site)
reactor.run()
