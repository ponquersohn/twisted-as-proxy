#!/usr/bin/python


import socket


class IcapClient:
	ICAP_SERVER="192.168.127.10"
	ICAP_PORT=1344
	ICAP_REQMOD_SERVICE = "/reqmod"
	ICAP_RESPMOD_SERVICE = "/respmod"

	def __init__(self, server=None, port=None, reqmod_service=None, respmod_service=None):
		self.request = None
		self.rtype = None
		self.icap_server = server or self.ICAP_SERVER
		self.icap_port = port or self.ICAP_PORT
		self.icap_reqmod_service = "icap://" + self.icap_server + "/" + (reqmod_service or self.ICAP_REQMOD_SERVICE)
		self.icap_respmod_service = "icap://" + self.icap_server + "/" + (respmod_service or self.ICAP_RESPMOD_SERVICE)

	
	def buildRequest(self, rtype, content=None):
		self.request = None
		self.rtype=rtype
		if rtype == 'OPTIONS':
			self.request = "OPTIONS %s ICAP/1.0\r\n" % (self.icap_reqmod_service)
            		self.request += "Host: localhost\r\n"
            		self.request += "Encapsulated: null-body=0\r\n"
            		self.request += "\r\n"

		return 0	

	def getOptions(self):
		self.buildRequest("OPTIONS")
		print "REQUEST:\n"
		print self.request
		print "ENDREQUEST\n"
		self.connect()
		self.send()
		self.getResponse()
		self.disconnect()

	def connect(self):
		self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connection.connect((self.icap_server, self.icap_port))

	def send(self):
		self.connection.send(self.request)

	def getResponse(self):
		for line in self.getLine():
			line = line.rstrip('\r\n')
			#print ("startA" )
			print (line)
			#print ( "Zkoniec")
			#if line in ['\n', '\r\n']:
			if line == "":
				print "END"
				break

	def getLine(self,recv_buffer=4096, delim='\n'):
		buffer = ''
		data = True
		while data:
			data = self.connection.recv(recv_buffer)
			buffer += data

			while buffer.find(delim) != -1:
				line, buffer = buffer.split('\n', 1)
				yield line
		return

	def disconnect(self):
		self.connection.close()
	
icap = IcapClient()
icap.getOptions()


