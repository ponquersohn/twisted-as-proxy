import icapclient
from pprint import pprint

conn = icapclient.ICAPConnection("192.168.127.10")

conn.request("RESPMOD", "/root/oper/body.172.eml", "RESPMOD")
resp = conn.getresponse()
