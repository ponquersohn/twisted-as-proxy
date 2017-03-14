#!/bin/env python
# -*- coding: utf8 -*-

import random
import SocketServer
import pprint
import md5
import subprocess
import zlib
import re
import StringIO
import struct
from libs.client.Sync import Sync
from libs.utils.wbxml import wbxml_parser
from libs.utils.as_code_pages import as_code_pages


from urlparse import urlparse, parse_qs
from dumper import dump_data_to_file

#from pyActiveSync.utils.wbxml import wbxml_parser
import xml.etree.ElementTree as ET

from pyicap import *


#create wbxml_parser test
cp, cp_sh = as_code_pages.build_as_code_pages()
parser = wbxml_parser(cp, cp_sh)



class ThreadingSimpleServer(SocketServer.ThreadingMixIn, ICAPServer):
    pass

class ICAPHandler(BaseICAPRequestHandler):

    def activesync_OPTIONS(self):
        self.set_icap_response(200)
        self.set_icap_header('Methods', 'RESPMOD')
        self.set_icap_header('Service', 'PyICAP Server 1.0')
        # Lech: must add preview to inspect headers before requesting content
        self.set_icap_header('Preview', '0')
        self.set_icap_header('Transfer-Ignore', 'jpg,jpeg,gif,png,swf,flv')
        self.set_icap_header('Transfer-Complete', '')
        self.set_icap_header('Max-Connections', '100')
        self.set_icap_header('Options-TTL', '3600')
        self.send_headers(False)

    def activesync_RESPMOD(self):
        #raw_input("press Enter")
        body = ''
        parsed_url = urlparse(self.enc_req[1])
        params = parse_qs(parsed_url.query)
        
        cmd = ''
        
        pprint.pprint (params)
        for k in params:
            if k.lower() == "cmd":
                cmd = params[k]
        
        
        
        #pprint.pprint(parsed_url)
        # check if we need more data because we expect preview
        if self.enc_res_headers.has_key("content-type") and "application/vnd.ms-sync.wbxml" in self.enc_res_headers["content-type"]:
            # bingo, we have AS message probably
            # lets set some values

            m = md5.new(pprint.pformat(vars(self))) # 
            print ("processing: " + m.hexdigest())
            base_file_path = "/root/oper/" + m.hexdigest()
            dump_data_to_file(base_file_path + '.vars', pprint.pformat(vars(self)))
        
            if self.preview:
                while True:
                    chunk = self.read_chunk()
                    if chunk == '':
                        break
                    body += chunk
                # LEch: we have read preview now lets decide if we want all the other stuff
                # todo: add condition for commands
                if self.has_body():
                    self.cont()
            
            if self.has_body:
                while True:
                    chunk = self.read_chunk()
                    body+=chunk
                    if chunk == '':
                        break

                # we have complete body
                if self.enc_headers.has_key("content-encoding") and "gzip" in self.enc_headers["content-encoding"]:
                    wbxml = zlib.decompress(body,16+zlib.MAX_WBITS)
                else:
                    wbxml = body

                dump_data_to_file(base_file_path + '.wbxml', wbxml)
            
                #xml = pnqwbxml2xml(wbxml)

                # inspect specific commands
                if cmd[0].lower() == 'sync':
                    #parser.encode(wapxml_req))
                    wapxml = parser.decode(wbxml)
                    s = Sync.parse(wapxml)
        
                
            # dummy return without adaptation    
            #self.no_adaptation_required()
            #return
            # dummy commit, will have to change it 
            
            self.set_icap_response(200)
            self.set_enc_status(' '.join(self.enc_res_status))
            for h in self.enc_res_headers:
                for v in self.enc_res_headers[h]:
                    self.set_enc_header(h, v)
            # send headers and return without any body changes
            self.send_headers(True)
            self.write_chunk(body)
            self.write_chunk('')
            
            return

        self.no_adaptation_required()
                
                



port = 12345

server = ThreadingSimpleServer(('', port), ICAPHandler)
try:
    while 1:
        server.handle_request()
except KeyboardInterrupt:
    print "Finished"
