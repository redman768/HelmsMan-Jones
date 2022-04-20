from RogueTraderShip import RogueTraderShip as Ship
from RogueTraderDiceRoller import RogueTraderDiceRoller
import pickle
from http.cookiejar import deepvalues
from builtins import str
class ShipManagerExecption(Exception):
    pass
class RogueTraderShipManager:
    def __init__(self,pDiceRoller):
        self.ships = {}
        self.diceRoller = pDiceRoller
        #PROD
        self.PICKLEFILENAME = ".\shipManager.save"
        try:
            self.loadState()
        except:
            pass
    async def repairAllShips(self, pModifiers, pNote, pChannel):
        returnString = ""
        for ship in self.ships.values():
            returnString = returnString + ship.getName() +": "
            if ship.isExtRepair():
                try:
                    returnString = returnString + await self.repairShip(ship, pModifiers, pNote + ship.getName(), pChannel)
                except Exception as e:
                    if str(e)!="Ship hull already full":
                        print("Raising from repairAllShips")
                        raise e
            elif ship.isRepairBay():
                amountRepaired =0
                try:
                    amountRepaired = ship.repair(7)
                    returnString = returnString + "repaired " + str(amountRepaired) +"!"
                except Exception as e:
                    if str(e) == 'Ship hull already full':
                        print("passing in repairShip")
                        returnString = returnString + "Already Full!"
                        pass
                    else:
                        print("raising in repairShip")
                        raise e 
            elif not ship.isExtRepair():
                returnString = returnString + "is not currently repairing."
            returnString = returnString + "\n"
        return returnString
    def setLocation(self,pShipName,pLocation):
        ship = self.getShip(pShipName).setLocation(pLocation)
        self.saveState()
        return pShipName + " is now located at "+pLocation
    def getLocation(self,pShipName):
        return self.getShip(pShipName).getLocation()
    def setShipInRepairBay(self,pShipName,pValue):
        ship = self.getShip(pShipName)
        ship.setIsInRepairBay(pValue)
        self.saveState()
        if pValue:
            return pShipName + " is now docked and repairing."
        else:    
            return pShipName + " is not docked and repairing anymore."
    def setExtendedRepair(self,pShipName,pValue):
        ship = self.getShip(pShipName)
        ship.setIsDoingExtRepair(pValue)
        self.saveState()
        if pValue:
            return pShipName + " is now repairing."
        else:    
            return pShipName + " is not repairing anymore."
    def saveState(self):
        pickleFile = open(self.PICKLEFILENAME,'wb')
        pickle.dump(self.ships,pickleFile)
        pickleFile.close()
    def loadState(self):
        pickleFile = open(self.PICKLEFILENAME,'rb')
        self.ships = pickle.load(pickleFile)
        pickleFile.close()
    def setshipCurrentHull(self,pShipName,pCurrentHull):
        self.getShip(pShipName).setCurrentHull(pCurrentHull)
        self.saveState()
    #pName,pShipClass,pCurrentHull,pMaxHull,pCrewRating
    def printShip(self,pShip):
        if isinstance(pShip,Ship):
            return pShip.printShip()
        else:
            return self.getShip(pShip).printShip()
    def removeShip(self,pShipName):
        try:
            del self.ships[pShipName]
            self.saveState()
            return "its gone now" 
        except:
            raise ShipManagerExecption("failed to remove,idk probably not a real ship")
    def addShip(self,pName,pShipClass,pCurrentHull,pMaxHull,pCrew):
        print(pName)
        #get ship will raise ship missing exception, catch it and add the ship
        try:
            if self.getShip(pName) != None:
                raise ShipManagerExecption("ship already exists")
        except ShipManagerExecption as e: 
            newShip = Ship(pName,pShipClass,pCurrentHull,pMaxHull,pCrew)
            self.ships[pName] = newShip
            self.saveState()
            return newShip
    def getShip(self,pShipName):
        if pShipName in self.ships:
            return self.ships[pShipName]
        else:
            for ship in self.ships.keys():
                print("########")
                print(ship)
                print(pShipName)
                print("########")
                if ship.upper() == pShipName.upper():
                    print("returning")
                    return self.ships[ship]
        raise ShipManagerExecption("That ship does not exist")
        
    def listShips(self):
        #message = 'name\tclass\thull\tRepair Status\tCrew Rating\tLocation'
        message = ''
        printString = ['name','class','hull','Repair Status','Crew Rating','Location']
        formatString = ""
        txtWidth = 25
        for entry in printString:
            formatString = "{:<"+str(txtWidth)+"}" + "{:<"+str(15)+"}" + "{:<"+str(10)+"}"+ "{:<"+str(20)+"}"+ "{:<"+str(15)+"}"+ "{:<"+str(txtWidth)+"}"
        print(formatString)
        message = formatString.format('name','class','hull','Repair Status','Crew Rating','Location')
        print(len(message))
        for ship in self.ships.values():
            message = message + '\n' + ship.printShip(txtWidth)
        print(message)
        return message
    def getShipCurrentHull(self,pShipName,pCurrentHull):
        ship = self.getShip(pShipName)
        return ship.getCurrentHull()
    def setShipCurrentHull(self,pShipName,pCurrentHull):
        ship = self.getShip(pShipName)
        self.saveState()
        return ship.setCurrentHull(pCurrentHull)
    async def repairShip(self,pShipName,pModifiers,pNote,pChannel=None):
        if isinstance(pShipName,Ship):
            shipToRepair = pShipName
        else:
            shipToRepair = self.getShip(pShipName)
        target = shipToRepair.getCrewRating()
        if pChannel == None:
            pChannel = self.diceRoller
        diceResults = await self.diceRoller.doStandardRoll(1,shipToRepair.getCrewRating()+pModifiers)
        returnString = ""
        isSucc = diceResults[0][0]
        if isSucc:
            d5RollResult = self.diceRoller.doAnyRoll(5)
            try:
                 returnString = "Repaired "+ str(shipToRepair.repair(int(d5RollResult))) + "!"
            except Exception as e:
                if str(e) == 'Ship hull already full':
                    returnString = "Ship Already full!"
                else:
                    print("raising in repairShip")
                    raise e
            self.saveState()
        else:
            returnString = "Failed to repair!"
        returnString = returnString + "(" +str(diceResults[0][2])
        if isSucc:
             returnString = returnString + "/" +str(d5RollResult) 
        returnString = returnString + ")"
        return returnString
if __name__ == '__main__':
    manager = RogueTraderShipManager()
    manager.addShip("test", "frigate", 50)
    manager.getShip("test").set
    print(manager.getShip("test").getName())
    print('why')