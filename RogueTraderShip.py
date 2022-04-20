class RogueTraderShip:
    class RogueTraderShipExecption(Exception):
        pass
    ##init and getters/setters##
    #pName,pShipClass,pCurrentHull,pmaxHull,pCrew
    def __init__(self,pName,pShipClass,pCurrentHull,pMaxHull,pCrewRating):
        self.maxHull = int(pMaxHull)
        self.name = pName
        self.shipClass = pShipClass
        self.crewRating = int(pCrewRating)
        self.currentHull = int(pCurrentHull)
        self.isInRepairBay = False
        self.isDoingExtRepair = False
        self.location = ""
    def __getattr__(self, name):
        if name == 'location':
            setattr(self,name,"")
        return object.__getattribute__(self, name)
    def getLocation(self):
        return self.location
    def setLocation(self,pLocation):
        self.location = pLocation
    def setIsInRepairBay(self,pValue):
        if self.isInRepairBay == pValue:
             raise RogueTraderShip.RogueTraderShipExecption("Its already set to that")
        elif self.isDoingExtRepair:
             raise RogueTraderShip.RogueTraderShipExecption("This ship is already doing extended repairs, can't do both")
        self.isInRepairBay = pValue
    def setIsDoingExtRepair(self,pValue):
        if self.isDoingExtRepair == pValue:
             raise RogueTraderShip.RogueTraderShipExecption("Its already set to that")
        elif self.isInRepairBay:
             raise RogueTraderShip.RogueTraderShipExecption("This ship is already repairing in dock, can't do both")
        self.isDoingExtRepair = pValue
    def isRepairBay(self):
        return self.isInRepairBay
    def isExtRepair(self):
        return self.isDoingExtRepair
    def setCurrentHull(self,pHull):
        self.currentHull = int(pHull)
        return self.currentHull
    def getCurrentHull(self):
        return self.currentHull
    def setMaxHull(self,pHull):
        self.maxHull = int(pHull)
    def getMaxHull(self):
        return self.maxHull 
    def setName(self,name):
        self.name = name
    def getName(self):
        return self.name 
    def setShipClass(self,pClass):
        self.shipClass = pClass
    def getShipClass(self):
        return self.shipClass
    def setCrewRating(self,pRating):
        self.crewRating = pRating
    def getCrewRating(self):
        return self.crewRating
    def getTechUse(self):
        return self.crewRating
    ##################################
    def repair(self,pAmount):
        if self.currentHull >= self.maxHull:
            print("Raising from repair")
            raise RogueTraderShip.RogueTraderShipExecption("Ship hull already full")
        elif self.currentHull + pAmount <= self.maxHull:
            self.currentHull =self.currentHull + pAmount
            return pAmount
        else:
            amount = self.maxHull - self.currentHull
            self.currentHull = self.maxHull
            return amount
    def printShip(self,pWidth=20):
        print(self.isInRepairBay)
        if self.isInRepairBay:
            repairStatus = "Repair Bay"
        elif self.isDoingExtRepair:
            repairStatus = "Extend Repairs"
        else:
            repairStatus = "Not Repairing"
        txtWidth = pWidth    
        formatString = "{:<"+str(txtWidth)+"}" + "{:<"+str(15)+"}" + "{:<"+str(10)+"}"+ "{:<"+str(20)+"}"+ "{:<"+str(15)+"}"+ "{:<"+str(txtWidth)+"}"
        print(len(formatString.format(self.name,self.shipClass,str(self.currentHull)+"/"+str(self.maxHull),repairStatus,str(self.crewRating),self.location)))
        return formatString.format(self.name,self.shipClass,str(self.currentHull)+"/"+str(self.maxHull),repairStatus,str(self.crewRating),self.location)
    
     