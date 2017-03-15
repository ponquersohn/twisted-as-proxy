#!/usr/bin/python
# from __future__ import absolute_import, division
# from pprint import pprint
# from twisted.python.compat import urllib_parse, urlquote
# from twisted.internet import reactor, ssl
# from twisted.internet.protocol import ClientFactory
# from twisted.web.resource import Resource
# from twisted.web.server import NOT_DONE_YET
# from twisted.web.http import HTTPClient, Request, HTTPChannel, _QUEUED_SENTINEL
# from twisted.web import proxy, server
# from twisted.web.proxy import ProxyClientFactory, ReverseProxyResource, ProxyClient
# from twisted.protocols.basic import LineReceiver
# import base64, urlparse, StringIO, uuid, sys
# import wbxml
# import subprocess
# import icapclient
# import uuid
# import xmltodict

from twisted.web import proxy, server
from twisted.web.proxy import ProxyClientFactory
from SSLActiveSyncProxyResource import SSLActiveSyncProxyResource
from twisted.internet import reactor


icap_server = "192.168.127.10"
icap_method = "RESPMOD"

#from dewbxml import wbxmlparser, wbxmlreader, wbxmldocument, wbxmlelement, wbxmlstring

#class DataReader(wbxmlreader):
#        def __init__(self, data):
#                self._wbxmlreader__bytes = StringIO.StringIO(data)


proxyResource = SSLActiveSyncProxyResource('outlook.office365.com', 443, '')
#proxyResource.setProxyClientFactoryClass(ActiveSyncProxyClientFactory)
site = server.Site(proxyResource)
reactor.listenTCP(8081, site)
reactor.run()
