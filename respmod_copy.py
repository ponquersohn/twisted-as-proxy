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
from urlparse import urlparse, parse_qs

from dewbxml import wbxmlparser, wbxmlreader, wbxmldocument, wbxmlelement, wbxmlstring

from pyActiveSync.utils.wbxml import wbxml_parser


import xml.etree.ElementTree as ET

from pyicap import *

def dump_data_to_file(filename, data):
    f = open(filename, "w")
    f.write(data)
    f.close()




class DataReader(wbxmlreader):
    def __init__(self, data):
        self._wbxmlreader__bytes = StringIO.StringIO(data)

#def pnqwbxml2xml(sourcexml):
#    cmd  = ['/usr/local/bin/wbxml2xml', '-', '-l', 'ACTIVESYNC', '-o', '-' ]
#    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
#                          stderr=subprocess.PIPE,
#                          stdin=subprocess.PIPE)
#    out, err = p.communicate(sourcexml)
#    #print "err: %s" % err
#    #print "out: %s" % out
#    return out
#    
#def pnqxml2wbxml(sourcexml):
#    cmd  = ['/usr/local/bin/xml2wbxml', '-a', '-', '-o', '-' ]
#    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
#                          stderr=subprocess.PIPE,
#                          stdin=subprocess.PIPE)
#    out, err = p.communicate(sourcexml)
#    #print "err: %s" % err
#    #print "out: %s" % out
#    return out    
    
    
#class DataReader(wbxmlreader):
#        def __init__(self, data):
#                self._wbxmlreader__bytes = StringIO.StringIO(data)

def convert_wbelem_to_dict(wbe):
        if isinstance(wbe, wbxmlelement):
                out_dict = {}
                k = wbe.name
                if len(wbe.children) == 1:
                        v = convert_wbelem_to_dict(wbe.children[0])
                else:
                        name_dupe = False
                        child_names = []
                        for child in wbe.children:
                                if isinstance(child, wbxmlelement):
                                        if child.name in child_names:
                                                name_dupe = True
                                                break
                                        child_names.append(child.name)
                        if not name_dupe:
                                v = {}
                                for child in wbe.children:
                                        v.update(convert_wbelem_to_dict(child))
                        else:
                                v = []
                                for child in wbe.children:
                                        v.append(convert_wbelem_to_dict(child))
                out_dict[k] = v
        else:
                return str(wbe).strip()
        return out_dict

def convert_array_to_children(in_elem, in_val):
        if isinstance(in_val, list):
                for v in in_val:
                        if len(v) > 2:
                                add_elem = wbxmlelement(v[0], page_num=v[2])
                        else:
                                add_elem = wbxmlelement(v[0], page_num=in_elem.page_num)
                        in_elem.addchild(add_elem)
                        convert_array_to_children(add_elem, v[1])
        elif isinstance(in_val, dict):
                print "FOUND OPAQUE THING",in_val
                in_elem.addchild(wbxmlstring(struct.pack(in_val["fmt"],in_val["val"]), opaque=True))
                print "OPAQUE PRODUCED",in_elem
        elif in_val != None:
                in_elem.addchild(wbxmlstring(in_val))

def convert_dict_to_wbxml(indict, default_page_num=None):
        wb = wbxmldocument()
        wb.encoding = "utf-8"
        wb.version = "1.3"
        wb.schema = "activesync"
        assert len(indict) == 1 # must be only one root element
        #print "Root",indict.keys()[0]
        if default_page_num != None:
                root = wbxmlelement(indict.keys()[0], page_num=default_page_num)
        else:
                root = wbxmlelement(indict.keys()[0])
        wb.addchild(root)
        convert_array_to_children(root, indict.values()[0])
        return wb



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
            base_file_path = "oper/" + m.hexdigest()
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

                wb = wbxmlparser()
                doc = wb.parse(DataReader(wbxml))
                res_dict = convert_wbelem_to_dict(doc.root)

                dump_data_to_file(base_file_path + '.xml', pprint.pformat(res_dict))

                # inspect specific commands
                if cmd[0].lower() == 'sync':

# <Sync xmlns="AirSync:">
#     <Collections>
#         <Collection>
#             <SyncKey>629054435</SyncKey>
#             <CollectionId>18</CollectionId>
#             <Status>1</Status>
#             <Responses>
#                 <Fetch>
#                     <ServerId>jxl0iRXUTU60IUTBkBXergAAAAABDI8ZdIkV1E1OtCFEwZAV3q4AAB_MYMA1</ServerId>
#                     <Status>1</Status>
#                     <ApplicationData>
#                         <To xmlns="Email:">&quot;Lech Lachowicz&quot; &lt;lech.lachowicz@simplicity-poland.pl&gt;</To>
#                         <From xmlns="Email:">&quot;Symantec&quot; &lt;support@feedback.satmetrix.com&gt;</From>
#                         <Subject xmlns="Email:">Symantec Corporation requests feedback for case 10128897</Subject>
#                         <Reply-To xmlns="Email:">&quot;reply-5314-186936343-265350361@feedback1.satmetrix.com&quot; &lt;reply-5314-186936343-265350361@feedback1.satmetrix.com&gt;</Reply-To>
#                         <DateReceived xmlns="Email:">2016-02-14T17:08:46.066Z</DateReceived>
#                         <DisplayTo xmlns="Email:">Lech Lachowicz</DisplayTo>
#                         <ThreadTopic xmlns="Email:">Symantec Corporation requests feedback for case 10128897</ThreadTopic>
#                         <Importance xmlns="Email:">1</Importance>
#                         <Read xmlns="Email:">0</Read>
#                         <Body xmlns="AirSyncBase:">
#                             <Type>4</Type>
#                             <EstimatedDataSize>24359</EstimatedDataSize>
#                             <Data>

                            # interestind data is in Fetch/ApplicationData/Body/Data, type means the type of message
                    # ET.register_namespace('',"http://schemas.microsoft.com")            
                    #  root = ET.fromstring(xml)
                    # for fetch in root.iter("Fetch"):
                    if res_dict["Sync"]["Collections"]["Collection"].has_key("Responses"):
                        for fetch in res_dict["Sync"]["Collections"]["Collection"]["Responses"]:
                            # get type, values 1:PlainText, 2: HTML, 3:RTF, 4:MIME
                            #type = fetch.get("body/type").text
                            #data = fetch.get("body/data").text
                            type = fetch["type"]
                            data = fetch["data"]
                        
                        #fetch.set("body/type", "1")
                        #fetch.set("body/data", "zmienione dane")
                    #xml = re.sub("<\/ns[0-9]+:","</", ET.tostring(root), flags = re.MULTILINE)
                    #xml = re.sub("<ns[0-9]+:","<", xml, flags = re.MULTILINE)
                    #nxml = '<!DOCTYPE ActiveSync PUBLIC "-//MICROSOFT//DTD ActiveSync//EN" "http://www.microsoft.com/">\n' + xml
                    #xml = nxml
                    wbxml = convert_dict_to_wbxml(res_dict)
                    #dump_data_to_file(base_file_path + '.modified.xml', xml)
                    #wbxml = pnqxml2wbxml(xml)
                    dump_data_to_file(base_file_path + '.modified.wbxml', wbxml)
                    body = wbxml
                
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
