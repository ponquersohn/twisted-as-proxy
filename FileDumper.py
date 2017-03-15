
import sys


class FileDumper:
    
    dump_path = "/root/oper"
   
    def __init__(self):
        return
    @staticmethod
    def dumpFile(direction, name, extension, data):
        # try:
        #     f = open(FileDumper.dump_path+"/" + "request." + name + "." + extension, "w")
        #     f.write(data)
        #     f.close()
        # except as detail:
        #     print "Unable to dump data to file", sys.exc_info()
        with open(FileDumper.dump_path+"/" + direction + "." + name + "." + extension, "w") as f:
            f.write(data)
            f.close()
            
