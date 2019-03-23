from Bug import Bug
from Trello import Trello
from conf.Config import Config
from utils import downloadFiles, readBugsFile, getBugs


### downloadUrls are the CSV files to read from, the key corresponds to the filename
#TODO put the downloadUrls in config
downloadUrls = {
        "main": "https://docs.google.com/spreadsheets/d/1VQuZoC6-i9wgtHAqk08IHUj7zXy1cvKjchNY8WExVXE/export?format=csv&id=1VQuZoC6-i9wgtHAqk08IHUj7zXy1cvKjchNY8WExVXE&gid=1404987435",
        "initial": "https://docs.google.com/spreadsheets/d/1VQuZoC6-i9wgtHAqk08IHUj7zXy1cvKjchNY8WExVXE/export?format=csv&id=1VQuZoC6-i9wgtHAqk08IHUj7zXy1cvKjchNY8WExVXE&gid=0",
        "debt": "https://docs.google.com/spreadsheets/d/1VQuZoC6-i9wgtHAqk08IHUj7zXy1cvKjchNY8WExVXE/export?format=csv&id=1VQuZoC6-i9wgtHAqk08IHUj7zXy1cvKjchNY8WExVXE&gid=1477013935"
        }

### files are saved to ./input_files. This dict specifies if there is are estimates in the spreadsheet or not
### and which column to pull that estimate from.
#TODO put all of this in config, also decouple from names?
files = {
        "./input_files/main.csv": {"hasEstimate": True, "estimateColumn": 9},
        "./input_files/initial.csv": {"hasEstimate": False},
        "./input_files/debt.csv": {"hasEstimate": False}
         }

config = Config()
bugData = {}

#### MAIN ###
# 1. Download files
# 2. Read files
# 3. Look up bug details from bugzilla
# 4. Create or update Trello cards as needed

downloadFiles(downloadUrls)
for filename, details in files.iteritems():
    if details.get("hasEstimate"):
        bugData = readBugsFile(bugData, filename, details.get("estimateColumn"))
    else:
        bugData = readBugsFile(bugData, filename)

bugs = getBugs(bugData)
trello = Trello()

for bug in bugs:
    card = trello.getCard(bug)
    if card is None:
        trello.createCardFromBug(bug)
    else:
        trello.updateCardFromBug(card, bug)

#TODO trello.cleanUp()
