#!/bin/env python
# -*- coding: utf8 -*-

import random
import SocketServer
import pprint

from pyicap import *

class ThreadingSimpleServer(SocketServer.ThreadingMixIn, ICAPServer):
    pass

class ICAPHandler(BaseICAPRequestHandler):

    def echo_OPTIONS(self):
	print "OPTIONS"
        self.set_icap_response(200)
        self.set_icap_header('Methods', 'RESPMOD')
        self.set_icap_header('Preview', '0')
        self.send_headers(False)

    def echo_RESPMOD(self):
        print "RESPMOD"
	pprint.pprint(vars(self))
        self.no_adaptation_required()

port = 12345

server = ThreadingSimpleServer(('0', port), ICAPHandler)
try:
    while 1:
        server.handle_request()
except KeyboardInterrupt:
    print "Finished"
