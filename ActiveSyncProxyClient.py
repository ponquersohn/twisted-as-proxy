import uuid
import xmltodict
import wbxml
import StringIO
import gzip
import zlib


from twisted.web.proxy import ProxyClientFactory, ReverseProxyResource, ProxyClient
from twisted.web.server import NOT_DONE_YET

from pprint import pprint

from pnqdewbxml import pnqwbxml2xml

def gunzip_text(text): 
    f = gzip.GzipFile(StringIO.StringIO(text)); 
    result = f.read(); 
    f.close(); 
    return result

    

class ActiveSyncProxyClient(ProxyClient):
    def logDebug(self, funct, message):
        print ("{}:SSLActiveSyncProxyClient.{}(): {}".format(self.uuid, funct, message))

    def __init__(self, *args, **kwargs):
        self.uuid = str(uuid.uuid1())
        self.resplength=0
        self._mybuffer = []
        self.encoding = ''
        self.ctype = ''
        self.headers_to_cache = {}
        self.commands = dict()
        ProxyClient.__init__(self,*args,**kwargs)
        self.logDebug("__init__", self.uuid + " args:")
        pprint(self.father.args) 
        self.logDebug("__init__", "done")

    def handleHeader(self, key, value):
        self.logDebug("handleHeader", "header: %s key: %s" % (key, value))
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

            
            f = open("/root/oper/" + self.uuid + cmd + "." + str(self.commands[cmd]) + '.wbxml', "w")
            f.write(b)
            f.close()


            xml = pnqwbxml2xml(b)
            #xml = wbxml.wbxml_to_xml(b)

            f = open("/root/oper/" + self.uuid + cmd + "." + str(self.commands[cmd]) + '.xml', "w")
            f.write(xml)
            f.close()

            doc = xmltodict.parse(xml)
            f = open("/root/oper/" + self.uuid + cmd + "." + str(self.commands[cmd]) + '.dict', "w")
            pprint(doc, f)
            f.close()

        
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
