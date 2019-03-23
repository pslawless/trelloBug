import csv
import requests

from Bug import Bug
from conf.Config import Config

config = Config()

def getCardNameFromBug(bug):
    return '[bug {}] - {}'.format(bug.number, bug.description)

def downloadFiles(urls):
    for key, url in urls.iteritems():
        filename = './input_files/{}.csv'.format(key)
        resp = requests.get(url)
        with open(filename, 'wb') as f:
            f.write(resp.content)

def readBugsFile(bugData, filename, estimateColumn=-1):
    with open(filename, 'r') as csvFile:
        csvreader = csv.reader(csvFile)
        headers = csvreader.next()

        currentEpic = "No Epic"
        for row in csvreader:
            column0 = row[0].strip()

            if column0.isdigit():
                if estimateColumn > -1:
                    bugData[column0] = {"epic": currentEpic, "estimate": row[config.estimateColumn], "altStatus": row[config.altStatusColumn]}
                else:
                    bugData[column0] = {"epic": currentEpic, "altStatus": row[config.altStatusColumn]}

            elif column0 != "" and column0.find("GH") < 0:
                currentEpic = column0
    return bugData

def getBugs(bugData):
    bugs = bugData.keys()
    url = 'https://bugzilla.mozilla.org/rest/bug?id={}'.format(", ".join(bugs))
    # print url
    resp = requests.get(url)
    if(resp.status_code != 200):
        print '\n*** ERROR: GET {} {}'.format(url, resp.status_code)
    resp_json = resp.json()
    bugs = []
    for b in resp_json["bugs"]:
        bugNum = str(b.get("id"))
        epic = bugData[bugNum].get("epic")
        altStatus = bugData[bugNum].get("altStatus")

        bug = Bug(bugNum, b.get("summary"), b.get("priority"), b.get("assigned_to"),
                  epic, b.get("status"), altStatus)
        if "estimate" in bugData[bugNum]:
            estimate = bugData[bugNum].get("estimate")
            bug.setEstimate(estimate)
        bugs.append(bug)

    return bugs
