import discord
import os
import random
import asyncio
import re
import math
from RogueTraderDiceRoller import RogueTraderDiceRoller
from RogueTraderShipManager import RogueTraderShipManager
class DiscordBotExecption(Exception):
    pass
class DiscordBot:
    client = discord.Client()
    clientToken=''
    diceRoller = RogueTraderDiceRoller(client)
    shipManager = RogueTraderShipManager(diceRoller)
    SHIPCOMMANDTYPE = 1
    LETTERCOMMANDTYPE = 0
    #constructor
    def __init__(self,clientToken):
        DiscordBot.clientToken=clientToken
        self.client=DiscordBot.client
        DiscordBot.client=self.client     
    def run(self):
        self.client.run(DiscordBot.clientToken)
    #read a value from the config file
    def getConfigValue(pValueToRead):
        configFile = open('helmsmanjones.conf','r')
        for line in configFile:
            if not line.startswith(pValueToRead):
                continue
            elif '=' not in line:
                raise DiscordBotExecption('config parameter found but can\'t read it correctly')
            return line.split('=')[1]  
        raise DiscordBotExecption('config parameter not found') 
    #get the command tokens
    def getTokens(pCommand):
        #wrap regex items in () to group them for later rtetrival
        commandRegex = re.compile('^([$])(\d*)(\D)(\d+)((\s*#)([\w|\W]*))?$')
        #shipKeywordRegex = re.compile('^([$])(\S*)(\s+)(\w*)(\s+)(\w*)((\s*#)([\w|\W]*))?$')
        shipKeywordRegex = re.compile('^([$])(\w+)([(\s+)-?(\w+)]*)((\s*#)([\w|\W]*))?')
        
        commandMatch = commandRegex.match(pCommand)
        if not commandMatch:
            shipKeyworkMatch = shipKeywordRegex.match(pCommand)
            if shipKeyworkMatch:
                returnMatch = shipKeyworkMatch
                matchType = DiscordBot.SHIPCOMMANDTYPE
            else:
                raise DiscordBotExecption("you messed up the command")
        else:
            matchType = DiscordBot.LETTERCOMMANDTYPE
            returnMatch = commandMatch
        print(returnMatch.groups())
        return matchType,returnMatch.groups()
    async def repairShip(pShipName,pModifiers):
        await DiscordBot.shipManager.repairShip(pShipName,pModifiers)
    #do the lock on roll
    async def doLockOnRoll(pNumberOfRolls,pTarget,pNote,pChannel):
        #TODO move thsi message creation to dice roller
        rollResults = await DiscordBot.diceRoller.doStandardRoll(pNumberOfRolls,pTarget)
        print(rollResults)
        message = ''
        for result in rollResults:
            bonus = 0
            if result[0]:
                #message = message + str(result[1]) + " degrees of Success\n"
                bonus = bonus + 5
                bonus = bonus + (math.floor(result[1]/2))*5
            message = message + "+" + str(bonus) + "("+str(result[2]) +")\n"
        return pNote +"\n"+message
        
    async def doStandardRoll(pNumberOfRolls,pTarget):
        rollResults = await DiscordBot.diceRoller.doStandardRoll(pNumberOfRolls,pTarget)
        #TODO move thsi message creation to dice roller
        print(rollResults)
        message =''
        for result in rollResults:
            if result[0]:
                message = message + str(result[1]) + " degrees of Success"
            else:
                message = message + str(result[1]) + " degrees of FAILURE"
            message = message + "(" +str(result[2]) +")\n"
        return message
    def getHelpMessage():
        return """Standard roll - $<num>r<target> ex $5r50
Lock on roll  - $<num>l<target> ex $5l50
Add ship      - $add <shipName> <shipClass> <currentHull> <maxHull> <crew>
Repair ship   - $repair <shipName> <repair mod> note: target is based on ship's crew, only put additional mods here. use all as shipNAme to repair all ships
Print ship    - $print <shipName> - note use all for <shipName> to print all ships
Set Attribute - $set <shipName> <attributeName> <value> 
    Attributes:
        repairbay - is this ship currently in a repair bay?(true/false)
        extrepair - is this ship currently doing extended repairs?(true/false)
        location  - where is this ship located?(any string)
You can add note by appending #<note>, doesn't show for all commands - ill fix it eventually. 
Also don't use spaces in your command arguments(except notes, thats fine).
                """
    #perform the command, branches for each command
    async def doCommand(channel,pCommand = []):
        if pCommand.rstrip().upper() == '$h'.upper():
            return DiscordBot.getHelpMessage()
        commandType,commandTokens = DiscordBot.getTokens(pCommand)
        print(commandTokens)
        if commandType == DiscordBot.LETTERCOMMANDTYPE:
            ##TODO: check command action
            commandAction = commandTokens[2]
            num = commandTokens[1]
            if num == '':
                num = 1
            num = int(num)
            target = int(commandTokens[3])
            note = commandTokens[6]
            if note == None:
                note = ''
            if commandAction.upper() == 'r'.upper():
                return await DiscordBot.doStandardRoll(num,target)
            elif commandAction.upper() == 'l'.upper():
                return await DiscordBot.doLockOnRoll(num,target,note,channel)  
        elif commandType == DiscordBot.SHIPCOMMANDTYPE:        
            commandAction = commandTokens[1]
            print(commandAction)
            commandArgs = commandTokens[2].split()
            if commandAction == 'set':
                shipName = commandArgs[0]
                setAttrib = commandArgs[1].upper()
                attribValue = commandArgs[2].upper()
                #build a dictionary of attribute to function mappings
                attribToFunctionMapping = {'extRepair'.upper():DiscordBot.shipManager.setExtendedRepair,
                                            'repairBay'.upper():DiscordBot.shipManager.setShipInRepairBay,
                                            'location'.upper():DiscordBot.shipManager.setLocation,
                                            'currentHull'.upper():DiscordBot.shipManager.setShipCurrentHull
                                            }
                if setAttrib == "extRepair".upper() or setAttrib == 'repairBay'.upper():
                    valueToSet = attribValue=='True'.upper() or attribValue=='t'.upper() or attribValue=='y'.upper() or attribValue=='yes'.upper()
                    falseValue = attribValue=='false'.upper() or attribValue=='f'.upper() or attribValue=='n'.upper() or attribValue=='no'.upper()
                else:
                    valueToSet = attribValue
                if not valueToSet and not falseValue:
                    raise DiscordBotExecption("wtf are you trying to set? give me a yes or no.")
                try:
                    return attribToFunctionMapping[setAttrib](shipName,valueToSet)
                except KeyError as e:
                    raise DiscordBotExecption("I think you messed up the attribute you want to set. try again.")
            elif commandAction == 'repair':
                #split on all space cuz i cant be bothered to get the regex exactly right                
                print(commandArgs)
                if len(commandArgs)<2:
                    raise DiscordBotExecption("think you missed something.")
                shipName = commandArgs[0]
                modifier = commandArgs[1]
                note = commandTokens[-1]
                if modifier == None:
                    modifier = 0
                else:
                    modifier = int(modifier)
                if note == None:
                    note =''
                #pShipName,pModifiers,pNote,pChannel=None
                if shipName.upper() == 'all'.upper():
                    return await DiscordBot.shipManager.repairAllShips(modifier,note,channel)
                else:
                    return await DiscordBot.shipManager.repairShip(shipName,modifier,note,channel)
            elif commandAction == 'add':
                if len(commandArgs) < 5:
                    raise DiscordBotExecption("I think you missed some shit, try it again.")
                shipName = commandArgs[0]
                shipClass = commandArgs[1]
                currentHull = commandArgs[2]
                maxHull = commandArgs[3]
                crew = commandArgs[4]
                return DiscordBot.shipManager.printShip(DiscordBot.shipManager.addShip(shipName,shipClass,currentHull,maxHull,crew))
            elif commandAction == 'print':
                if len(commandArgs) < 1:
                     raise DiscordBotExecption("I think you missed some shit, try it again.")
                shipName = commandArgs[0]
                if shipName.upper() == 'all'.upper():
                    return  DiscordBot.shipManager.listShips()
                else: 
                    return DiscordBot.shipManager.printShip(shipName)
            elif commandAction == 'remove':
                if len(commandArgs) < 1:
                     raise DiscordBotExecption("I think you missed some shit, try it again.")
                shipName = commandArgs[0]
                return DiscordBot.shipManager.removeShip(shipName)
    @client.event
    async def on_ready():
        print('We have logged in as {0.user}'.format(DiscordBot.client))
        
        ##DiscordBot.repairShip('test',0)
    async def doCommands(pChannel):
        commands = ["$add Allesunders_Johnson Battleship 0 90 70"
        ,"$set Allesunders_Johnson repairbay true"
        
        ,"$add Feminine_Johnson Battlecruiser 26 66 60"
        ,"$set Feminine_Johnson repairbay true"
        
        ,"$add Tempest-Heart Battlecruiser 65 66 60"
        ,"$set Tempest-Heart extrepair true"
        
        ,"$add Modest_Johnson Cruiser 0 70 30"
        ,"$set Modest_Johnson extrepair true"
        
        ,"$add Allesunders_Might LCruiser 0 60 30"
        ,"$set Allesunders_Might extrepair true"
        
        ,"$add Explosive_Johnson LCruiser 0 56 30"
        ,"$set Explosive_Johnson repairbay true"
        
        ,"$add Dauntless_Johnson LCruiser 0 60 30"
        ,"$set Dauntless_Johnson repairbay true"
        
        ,"$add Soft_Johnson Frigate 0 40 30 "
        ,"$set Soft_Johnson extrepair true"
        
        ,"$add Eclipse_Of_Zeabor Frigate 0 40 30"
        ,"$set Eclipse_Of_Zeabor repairbay true"
        
        ,"$add Tropicannon GCruiser 4 85 70"
        ,"$set Tropicannon repairbay true"
        
        ,"$add Snee_Key Cruiser 32 69 70"
        ,"$set Snee_Key repairbay true"
        
        ,"$add Leonardo Cruiser 11 76 60"
        ,"$set Leonardo extrepair true"
        
        ,"$add Donatello Cruiser 24 76 60"
        ,"$set Donatello extrepair true"
        
        ,"$add Michelangelo Cruiser 11 72 60"
        ,"$set Michelangelo extrepair true"
        
        ,"$add Repugnant_Leviathan GCruiser 53 91 60"
        ,"$set Repugnant_Leviathan extrepair true"
        
        ,"$add Proxima_Vinco Cruiser 48 70 60"
        ,"$set Proxima_Vinco extrepair true"
        
        ,"$add Vengeful_Johnson Cruiser 54 68 65"
        ,"$set Vengeful_Johnson extrepair true"
        
        ,"$add Allesunders_Majesty Cruiser 0 69 65"
        ,"$set Allesunders_Majesty extrepair true"
        
        ,"$add Libertatem GCruiser 55 85 60"
        ,"$set Libertatem extrepair true"
        
        ,"$add Romulus LCruiser 40 60 60"
        ,"$set Romulus extrepair true"
        
        ,"$add Remus LCruiser 41 60 60"
        ,"$set Remus extrepair true"
        
        ,"$add Rafael LCruiser 28 76 60"
        ,"$set Rafael extrepair true"
        
        ,"$add Hammer_of_Iron LLCruiser 0 65 60"
        ,"$set Hammer_of_Iron extrepair true"
        
        ,"$add Valorous_Sacrament Cruiser 50 68 60"
        ,"$set Valorous_Sacrament extrepair true"]
        for entry in commands:
            await pChannel.send(entry)
            commandResponse = await DiscordBot.doCommand(pChannel,entry)
            await pChannel.send(commandResponse)
        await pChannel.send("init complete")
    @client.event
    async def on_message(message):
        if message.author == DiscordBot.client.user:
            return
        if message.content.startswith('%init'):   
            await DiscordBot.doCommands(message.channel)
        if message.content.startswith('%test'):
            returnString = ''   
            DiscordBot.doStandardRoll(100,50)
        if message.content.startswith('$'):
            #await message.channel.send(await getTokens(message.content))
            try:
                #diceRoller = RogueTraderDiceRoller(DiscordBot.client)
                commandResponse = str(await DiscordBot.doCommand(message.channel,message.content))
                if len(commandResponse) > 2000:
                    trimmedResponse = "```"
                    for line in commandResponse.splitlines(True):
                        trimmedResponse =  trimmedResponse + line
                        if len(trimmedResponse) > 1500:
                            await message.channel.send(trimmedResponse+"```")
                            trimmedResponse = "```"
                    #send the last remaining message
                    await message.channel.send(trimmedResponse+"```")
                else:
                    await  message.channel.send("```" +commandResponse+ "```") 
            except Exception as e:
                #raise
                #PROD
                await message.channel.send(e)
#PROD

apiToken = DiscordBot.getConfigValue('apiToken')
bot=DiscordBot(apiToken)
if __name__ == '__main__':
    bot.run()
    
