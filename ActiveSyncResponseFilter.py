
class ActiveSyncResponseFilter:

    
    uuid = "uuid not defined yet"
    
    def logDebug(self, funct, message):
        cname = "ActiveSyncResponseFilter";
        print ("{}:      {}.{}(): {}".format(self.uuid, cname, funct, message))

    
    def __init__(self, uuid):
        self.uuid = uuid
        self.logDebug("__init__", "Called")
        return
    
    def filterCommand(self, command, request_headers, response_headers, document):
        self.logDebug("filterCommand", "Called")
        if command in self.commandsToFilter:
            return self.commands[command](self,request_headers, response_headers, document)
        
        return document
        
    def filterSyncCommand(self, request_headers, response_headers, document):
        self.logDebug("filterSyncCommand", "Called")
        return document
        
    def filterPingCommand(self, request_headers, response_headers, document):
        self.logDebug("filterSyncCommand", "Called")
        return document        
        
        
    commandsToFilter = ["Sync", "Ping"]
    commands = {"Sync": filterSyncCommand,
                "Ping": filterPingCommand}
