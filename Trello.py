import requests
import json

from utils import getCardNameFromBug
from conf.Config import Config

config = Config()

class Trello:
    def __init__(self):
        self.cards = []
        self.lists = []
        self.members = []
        self.labels = []
        self.board_id = config.trelloBoardId
        self.api_key = config.trelloApiKey
        self.token = config.trelloToken
        self.updatedCards = []
        self.createdCards = []
        self.colors = {"yellow": True, "purple": True, "blue": True, "red": True, "green": True, "orange": True,
          "sky": True, "pink": True, "lime": True}

        self.batchLoad()

    def batchLoad(self):
        urls = '/boards/{}/lists?cards=none,/boards/{}/cards,/boards/{}/members,/boards/{}/labels'.format(
                self.board_id, self.board_id, self.board_id, self.board_id)
        batchUrl = 'https://api.trello.com/1/batch/?urls={}&key={}&token={}'.format(urls, self.api_key, self.token)
        response = requests.get(batchUrl)

        i = 0
        things = ["lists", "cards", "members", "labels"]
        for thing in response.json():
            if i >= len(things):
                print "Error: more results than expected"
            for key, value in thing.iteritems():
                if key == "200":
                    if things[i] == "cards":
                        self.cards = value
                    elif things[i] == "lists":
                        self.lists = value
                    elif things[i] == "members":
                        self.members = value
                    elif things[i] == "labels":
                        self.labels = value
            i = i+1

    def getListId(self, status):
        for li in self.lists:
            if status and status.find(li.get("name")) > -1:
                return li.get("id")
        return None

    def getMemberId(self, bugMail):
        # [{u'username': u'patricialawless1', u'fullName': u'Patricia Lawless', u'id': u'5c65f7e5f2d94e1a873f4085'}]
        peopleMap = config.peopleMap
        for member in self.members:
            if bugMail == "nobody@mozilla.org":
                return None
            elif bugMail in peopleMap and member.get("username") == peopleMap[bugMail]:
                return member.get("id")

    def getLabelId(self, labelName, isEstimate=False):
        found = None
        for label in self.labels:
            if label.get("name") == labelName:
                found = label
        if not found:
            found = self.createLabel(labelName, isEstimate)
        return found

    def getColor(self, isEstimate=False):
        if isEstimate:
            return "black"

        for k,v in self.colors.iteritems():
            if v:
                self.colors[k] = False
                return k
        return "null"

    def createLabel(self, labelName, isEstimate=False):
        url = "https://api.trello.com/1/labels"
        color = "black"
        if not isEstimate:
            color = self.getColor(isEstimate)

        boardId = self.getBoardId()
        querystring = {"name": labelName, "color": color, "idBoard": boardId, "key": self.api_key, "token": self.token}
        response = requests.request("POST", url, params=querystring)

        if response.status_code != 200:
            print "Error creating Label: " + response.text + "\nquerystring: " + json.dumps(querystring)
        newLabel = response.json()
        self.labels.append(newLabel)
        return newLabel

    def getCard(self, bug):
        for card in self.cards:
            #check by bug number only, in case the bug summary changes
            if card.get("name").find(str(bug.number)) > -1:
                return card
        return None

    def getBoardId(self):
        url = 'https://api.trello.com/1/boards/{}'.format(config.trelloBoardId)
        querystring = {"key": self.api_key, "token": self.token}
        response = requests.request("GET", url, params=querystring)
        if response.status_code != 200:
            print "Error getting BoardId: " + response.text + "\nurl:" + url

        board = response.json()
        return board.get("id")

    def getCardDetailsFromBug(self, bug):
        cardName = getCardNameFromBug(bug)
        listId = self.getListId(bug.status)
        assignee = self.getMemberId(bug.assignee)
        label = self.getLabelId(bug.epic)
        labelList = [label.get("id")]
        if bug.estimate:
            estimateLabel = self.getLabelId(bug.estimate.strip(), isEstimate=True)
            labelList.append(estimateLabel.get("id"))

        return cardName, listId, assignee, labelList

    def createCardFromBug(self, bug):
        cardName, listId, assignee, labelList = self.getCardDetailsFromBug(bug)

        url = "https://api.trello.com/1/cards"
        querystring = {"name": cardName, "desc": bug.url, "idList": listId, "idLabels": labelList,
                       "keepFromSource":"all","key": self.api_key, "token": self.token}
        if assignee:
            querystring["idMembers"] = assignee

        response = requests.request("POST", url, params=querystring)
        if response.status_code != 200:
            print "Error creating Card: " + response.text + "\nquerystring: " + json.dumps(querystring)
        else:
            self.createdCards.append(response)

    def updateCardFromBug(self, card, bug):
        cardName, listId, assignee, labelList = self.getCardDetailsFromBug(bug)
        querystring = {}

        if cardName != card.get("name"):
            querystring["name"] = cardName

        doNotMoveIds = [self.getListId(x) for x in config.doNotMoveList]
        currentList = card.get("idList")
        if listId != currentList and currentList not in doNotMoveIds:
            querystring["idList"] = listId

        if assignee and assignee not in card.get("idMembers"):
            querystring["idMembers"] = assignee

        if labelList != card.get("idLabels"):
            querystring["idLabels"] = labelList

        # only update if something changed.
        if bool(querystring):
            print "Update: done"
            querystring["key"] = self.api_key
            querystring["token"] = self.token
            url = 'https://api.trello.com/1/cards/{}'.format(card.get("id"))
            response = requests.request("PUT", url, params=querystring)
            self.updatedCards.append(response)
            if response.status_code != 200:
                print "Error updating Card: " + response.text + "\nquerystring: " + json.dumps(querystring)

    #TODO... remove cards that were deleted from spreadsheet
    #def cleanUp(self):
    #    allCards = self.createdCards + self.updatedCards
    #    print "allCards: " + ", ".join(allCards)
    #    print "cards from Trello:" + ", ".join(self.cards)
        #cardsToDelete = list(set(allCards) - set(self.cards))
        #if len(cardsToDelete) > 0:
            # archive cards
        #    for card in cardsToDelete:
        #        querystring = {"closed": "true", "key": self.api_key, "token": self.token}
        #        url = 'https://api.trello.com/1/cards{}'.format(card.get("id"))
        #        print "Card to Archive:" + querystring + " -- " + url
                #response = requests.request("PUT", url, querystring)
                #print response.text
