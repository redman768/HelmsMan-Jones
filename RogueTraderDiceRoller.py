import random
import os as os
class DiceRollerException(Exception):
    pass
class RogueTraderDiceRoller:
    discordClient = None
    LOCKONNOTEINDEX = 2
    LOCKONTARGETINDEX = 1
    DICEPARSERRESULTINDEX = 2
    def __init__(self,pDiscordClient):
        RogueTraderDiceRoller.discordClient = pDiscordClient
    def setChannel(self,pChannel):
        self.channel = pChannel
    def getChannel(self):
        return self.channel
    #caluclate degrees of success. (target-roll)/10 dropping decimal. Ex. 85-100=-15/10=-1.5=-1
    def getDegreesOfSucc(self,pTarget,pRoll):
        print(pRoll)
        diff = int(pTarget) - int(pRoll)
        degrees = int((diff/10))
        succ = int(pRoll)<=int(pTarget)
        return degrees,succ
    async def executeDiscordCommand(self,pCommand):
        pass
    def doAnyRoll(self,pSidesOfDice):
        rollResults = random.SystemRandom().randint(1, pSidesOfDice)
        return rollResults
    #do the roll and return the result. returns a list of 2 element lists,element 1=failure or success, element 2 = degrees 
    async def doStandardRoll(self,pNumOfRolls,pTarget):
        
        degreesList = []
        for rollResult in range(0,pNumOfRolls):
            indRollResult = self.doAnyRoll(100)
            degrees,succ = self.getDegreesOfSucc(pTarget,indRollResult)
            if not succ:
                degreesList.append([False,degrees*-1,indRollResult])
            else:
                degreesList.append([True,degrees,indRollResult])
        return degreesList