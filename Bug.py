from conf.Config import Config

class Bug:
    def __init__(self, number, description, priority, assignee, epic, status, altStatus=None, estimate=None):
        self.number = number
        self.description = description
        self.priority = priority
        self.assignee = assignee
        self.epic = epic
        self.status = status
        self.estimate = estimate
        self.url = 'https://bugzilla.mozilla.org/show_bug.cgi?id={}'.format(number)
        self.config = Config()
        self.setStatus(altStatus)

    def setEstimate(self, estimate):
        self.estimate = estimate

    def setStatus(self, altStatus):
        # Bug Flow: New/Unconfirmed -> Assigned -> In Review -> Reviewed -> Landed/Resolved
        newStatuses = self.config.newStatuses
        landedStatuses = self.config.landedStatuses

        if self.status in newStatuses:
            self.status = "NEW"
        elif self.status in landedStatuses:
            self.status = "LANDED"
        elif self.status != altStatus and self.status == "ASSIGNED":
            #check spreadsheet status and return appropriate one
            self.status = altStatus

    def __repr__(self):
        return "Bug: " + self.number + ", status="+ self.status if self.status else "no status"

    def __str__(self):
        return "Bug: " + self.number + ", status="+ self.status
        #return 'Bug(number={}, description={}, priority={}, assignee={}, epic={}, status={}, estimate={}, url={})'.format(
        #        self.number, self.description, self.priority, self.assignee, self.epic, self.status, self.estimate,
        #        self.url)
