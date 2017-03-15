
import xmltodict
import wbxml
import StringIO
import gzip
import zlib


from twisted.web.proxy import ProxyClientFactory, ReverseProxyResource, ProxyClient
from twisted.web.server import NOT_DONE_YET

import pprint
from FileDumper import FileDumper

from pnqdewbxml import pnqwbxml2xml

def gunzip_text(text): 
    f = gzip.GzipFile(StringIO.StringIO(text)); 
    result = f.read(); 
    f.close(); 
    return result

    

class ActiveSyncProxyClient(ProxyClient):
    uuid = "uuid not defined yet"
    def logDebug(self, funct, message):
        cname = "SSLActiveSyncProxyClient";
        print ("{}:      {}.{}(): {}".format(self.uuid, cname, funct, message))

    def __init__(self, uuid, *args, **kwargs):
        self.uuid = uuid
        self.logDebug("__init__", "Called")
        self.resplength=0
        self._mybuffer = []
        self.encoding = ''
        self.ctype = ''
        self.headers_to_cache = {}
        self.commands = dict()
        ProxyClient.__init__(self,*args,**kwargs)
        self.logDebug("__init__", "ARGS: " + pprint.pformat(self.father.args, width=99999999))
        
        self.logDebug("__init__", "done")

    def handleHeader(self, key, value):
        self.logDebug("handleHeader", "Processig header: %s: %s" % (key, value))
        if key == "Content-Type":
            self.replace = True
            self.ctype = value
        if key == "Content-Encoding":
            self.encoding = value
        self.headers_to_cache[key] = value
        
        ProxyClient.handleHeader(self, key, value)
        self.logDebug("handleHeader", "done")

    def handleResponsePart(self, buffer):
        self.logDebug("handleResponsePart", "buflen: %d" %(len(buffer)))
        self._mybuffer.append(buffer)
        self.resplength+=len(buffer)
        self.logDebug("handleResponsePart", "NOT_DONE_YET")
        return NOT_DONE_YET

    def handleResponseEnd(self):
        if self._mybuffer is not None:
            b = ''.join(self._mybuffer)

        self.logDebug("handleResponseEnd", "handleResponseEnd resplength: %d b_length: %d" %(self.resplength, len(b)))
        if self.ctype == 'application/vnd.ms-sync.wbxml' and self.father.args.has_key('Cmd') and len(b)>0 :
            self.logDebug("handleResponseEnd",  "Found Content-Type: %s" % self.ctype)
            self.logDebug("handleResponseEnd",  "Processing command: %s" % self.father.args['Cmd'][0])
            cmd = self.father.args['Cmd'][0]
            #xml = wbxml.wbxml_to_xml(b)

            if cmd in self.commands:
                self.commands[cmd]=self.commands[cmd]+1
            else:
                self.commands[cmd]=1
            
            if self.encoding == 'gzip':
                self.logDebug("handleResponseEnd", "It seems the response is gziped... unzipping.")
                #b = gunzip_text(b)
                b = zlib.decompress(b, 16+zlib.MAX_WBITS)

            dump_file_prefix = self.uuid + cmd + "." + str(self.commands[cmd])
            FileDumper.dumpFile("response", dump_file_prefix , "wbxml", b)
            

            xml = pnqwbxml2xml(b)
            #xml = wbxml.wbxml_to_xml(b)
            FileDumper.dumpFile("response", dump_file_prefix , "xml", xml)
      
            doc = xmltodict.parse(xml)
            FileDumper.dumpFile("response", dump_file_prefix , "dict", pprint.pformat(doc))
        
        if len(b) > 0:
            for buff in self._mybuffer:
                ProxyClient.handleResponsePart(self,buff)
            ProxyClient.handleResponsePart(self,"")    
        else:
            ProxyClient.handleResponsePart(self,"")
        #ProxyClient.handleResponsePart(self,b)
        self.logDebug("handleResponseEnd", "resplength: %d b_length: %d" %(self.resplength, len(b)))
        self.logDebug("handleResponseEnd", "Finished")
        self.__buffer = None
    #ProxyClient.handleResponseEnd()
        #self.handleResponseEnd(self)
        self.logDebug("handleResponseEnd", "NOT_DONE_YET")
        return NOT_DONE_YET
