import ConfigParser

class Config:
    def __init__(self):
        self.config = ConfigParser.ConfigParser()
        self.config.read('conf/config.ini')

    @property
    def estimateColumn(self):
        return int(self.config.get("Spreadsheet", "estimateColumn"))

    @property
    def altStatusColumn(self):
        return int(self.config.get("Spreadsheet", "altStatusColumn"))

    @property
    def trelloBoardId(self):
        return self.config.get("Trello", "board_id")

    @property
    def trelloApiKey(self):
        return self.config.get("Trello", "api_key")

    @property
    def trelloToken(self):
        return self.config.get("Trello", "token")

    @property
    def doNotMoveList(self):
        dnm = self.config.get("Trello", "doNotMoveList")
        return dnm.split(",")

    @property
    def peopleMap(self):
        pp = self.config.get("People", "map")
        ppList = pp.split(",")
        return dict(p.strip().split(':') for p in ppList)

    @property
    def newStatuses(self):
        ns = self.config.get("Bugzilla", "newStatuses")
        return ns.split(",")

    @property
    def landedStatuses(self):
        ls = self.config.get("Bugzilla", "landedStatuses")
        return ls.split(",")

#TODO
#    @property
#    def isDownload(self):
#        return bool(self.config.get("Spreadsheet", "isDownload"))
#
#    @property
#    def files(self):
#        numFiles = int(self.config.get("Spreadsheet", "numberOfFiles"))
#        print "numFiles="+str(numFiles)
#        i=1
#        files = []
#        while i <= numFiles:
#            files.append(self.config.get("Spreadsheet", "file"+str(i)).strip())
#            i=i+1
        return files
