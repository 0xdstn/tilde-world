#!/usr/bin/env python3

import os
import getpass
from pathlib import Path

username = getpass.getuser()

rootDir = str(Path.home()) + '/.world/'
locPath = rootDir + 'loc'
configPath = rootDir + 'config'
roomsPath = rootDir + 'rooms/'
statePath = rootDir + 'state/'
inventoryPath = rootDir + 'inventory'

westDirections = ['l','w','left','west']
eastDirections = ['r','e','right','east']
northDirections = ['u','n','up','north']
southDirections = ['d','s','down','south']
validDirections = westDirections + eastDirections + northDirections + southDirections

class Room:
    def __init__(self):
        self.name = ''
        self.desc = ''
        self.objects = []
        self.exits = []
        self.key = ''
        self.user = ''
        self.x = ''
        self.y = ''

    def setItem(self, key, val):
        if key == 'name': self.name = val
        elif key == 'key': self.key = val
        elif key == 'desc': self.desc = val
        elif key == 'objects': self.objects = val

class Object:
    def __init__(self):
        self.id = ''
        self.name = ''
        self.desc = ''
        self.grab = False
        self.hidden = False
        self.props = []
        self.actions = []

    def setItem(self, key, val):
        if key == 'id': self.id = val
        elif key == 'name': self.name = val
        elif key == 'desc': self.desc = val
        elif key == 'grab': self.grab = val == 'true'
        elif key == 'hidden': self.hidden = val == 'true'
        elif key == 'props': self.props = val
        elif key == 'actions': self.actions = val

class Item:
    def __init__(self):
        self.id = ''
        self.name = ''
        self.desc = ''

class Action:
    def __init__(self):
        self.triggers = []
        self.instructions = []

    def set(self, triggers, instructions):
        self.triggers = triggers
        self.instructions = instructions

class Prop:
    def __init__(self):
        self.key = ''
        self.value = ''

    def set(self, key, val):
        self.key = key
        self.value = val

class State:
    def __init__(self):
        self.room = Room()
        self.locX = 0
        self.locY = 0
        self.inventory = []

def getPropFileName(user, x, y, obj, prop):
    propFileName = statePath
    propFileName += str(x).replace('-','n') + '_'
    propFileName += str(y).replace('-','n') + '_'
    propFileName += obj.id.replace(' ','-') + '_' 
    propFileName += prop + '.txt'

    return propFileName

def getInventory():
    inventory = []
    inventoryFile = open(inventoryPath,'r')
    inventoryLines = [x.strip('\n') for x in inventoryFile]
    inventoryFile.close()
    for line in inventoryLines:
        item = Item()
        info = line.split(' : ')
        if len(info) == 3:
            item.id = info[0]
            item.name = info[1]
            item.desc = info[2]
            inventory.append(item)
    return inventory


def getRoom(x, y):
    users = os.listdir('/home')

    room = Room()
    objects = []
    actions = []
    props = []

    for u in users:
        roomPath = roomsPath.replace(username,u) + str(x).replace('-','n') + '_' + str(y).replace('-','n')
        if os.path.exists(roomPath):
            room.user = u
            room.x = x
            room.y = y
            roomData = open(roomPath, 'r')
            roomLines = [x.strip('\n') for x in roomData]
            curObj = Object()
            curProp = Prop()
            curAction = Action()
            inProp = False
            inAction = False
            for line in roomLines:
                if line[0] != ' ':
                    inProp = False
                    inAction = False
                    pieces = line.split(' : ')
                    if len(pieces) == 2:
                        room.setItem(pieces[0].lower(),pieces[1])
                else:
                    if line == '  -':
                        if inAction:
                            curObj.actions.append(curAction)
                            curAction = Action()
                            inAction = False
                        if curObj.name != '':
                            objects.append(curObj)
                        curObj = Object()
                    elif ' : ' in line:
                        pieces = line.strip().split(' : ')
                        curObj.setItem(pieces[0].lower(),pieces[1])
                    elif line.startswith('    PROPS'):
                        if inAction:
                            curObj.actions.append(curAction)
                            inAction = False
                        inProp = True
                    elif line.startswith('    ACTIONS'):
                        if inProp:
                            curObj.props.append(curProp)
                            inProp = False
                        inAction = True
                    elif inProp:
                        pieces = line.strip().split('=')
                        propFileName = getPropFileName(u, x, y, curObj, pieces[0])

                        if os.path.exists(propFileName):
                            propFile = open(propFileName,'r')
                            curProp.set(pieces[0], propFile.read().strip())
                            propFile.close()
                        else:
                            propFile = open(propFileName,'w')
                            curProp.set(pieces[0], pieces[1])
                            propFile.write(pieces[1])
                            propFile.close()
                    elif inAction:
                        if line.startswith('        '):
                            curAction.instructions.append(line[8:])
                        elif line.startswith('      '):
                            if len(curAction.triggers):
                                curObj.actions.append(curAction)
                            curAction = Action()
                            curAction.triggers = line[6:].split('|')
            if inAction:
                curObj.actions.append(curAction)
            if inProp:
                curObj.props.append(curProp)
            if curObj.name != '':
                objects.append(curObj)
            room.setItem('objects',objects)

        if 'north' not in room.exits:
            tmpX = x
            tmpY = y + 1
            northPath = roomsPath.replace(username,u) + str(tmpX).replace('-','n') + '_' + str(tmpY).replace('-','n')
            if os.path.exists(northPath):
                room.exits.append('north')
        
        if 'south' not in room.exits:
            tmpX = x
            tmpY = y - 1
            southPath = roomsPath.replace(username,u) + str(tmpX).replace('-','n') + '_' + str(tmpY).replace('-','n')
            if os.path.exists(southPath):
                room.exits.append('south')

        if 'east' not in room.exits:
            tmpX = x + 1
            tmpY = y
            eastPath = roomsPath.replace(username,u) + str(tmpX).replace('-','n') + '_' + str(tmpY).replace('-','n')
            if os.path.exists(eastPath):
                room.exits.append('east')

        if 'west' not in room.exits:
            tmpX = x - 1
            tmpY = y
            westPath = roomsPath.replace(username,u) + str(tmpX).replace('-','n') + '_' + str(tmpY).replace('-','n')
            if os.path.exists(westPath):
                room.exits.append('west')
    return room

def updateLoc(x, y):
    locFile = open(locPath, 'r+')
    locFile.truncate(0)
    locFile.write(str(x) + ',' + str(y))
    locFile.close()

def prnt(value):
    if isinstance(value,str):
        print('  ' + value)
    else:
        for x in value:
            print('  ' + x)

def inInventory(key):
    global state
    found = False
    for item in state.inventory:
        if item.id == key:
            found = True
    return found

def addToInventory(obj):
    global state

    owned = inInventory(obj.id)

    if owned:
        prnt('You already have one of these')
    else:
        inventoryFile = open(inventoryPath,'a')
        inventoryFile.write(obj.id + ' : ' + obj.name + ' : ' + obj.desc + "\n")
        inventoryFile.close()
        item = Item()
        item.id = obj.id
        item.name = obj.name
        item.desc = obj.desc
        state.inventory.append(item)
        prnt('You obtain "' + obj.name + '"')

def removeFromInventory(key):
    global state
    
    owned = inInventory(key)

    if not owned:
        prnt('This item is not in your inventory')
    else:
        inventoryFile = open(inventoryPath,'w')
        for item in state.inventory:
            if item.id == key:
                state.inventory.remove(item)  
                prnt('You drop "' + item.name + '"')
            else:
                inventoryFile.write(item.id + ' : ' + item.name + ' : ' + item.desc + "\n")
        inventoryFile.close()

def lookObj(cmd):
    item = cmd[5:]
    found = False
    for obj in state.room.objects:
        if item == obj.id:
            found = True
            desc = obj.desc
            if len(obj.props):
                for prop in obj.props:
                    desc = desc.replace('[' + prop.key + ']', prop.value)
            prnt(desc)
            if len(obj.actions):
                print('')
                actionsOut = ['You can:']
                for actn in obj.actions:
                    actionsOut.append('- ' + actn.triggers[0])
                prnt(actionsOut)

    if not found:
        prnt('Object not found')

def grabObj(cmd):
    item = cmd[5:]
    found = False
    for obj in state.room.objects:
        if item == obj.id:
            found = True
            if obj.grab:
                addToInventory(obj)
            else:
                prnt('This object is not attainable')

    if not found:
        prnt('Object not found')

def dropObj(cmd):
    item = cmd[5:]
    removeFromInventory(item)

def look():
    prnt(state.room.desc)

    if len(state.room.objects):
        print('')

        objOut = ["You see:"]
        for obj in state.room.objects:
            if not inInventory(obj.id) and not obj.hidden:
                objText = '- '
                objText += ('An ' if obj.name[0] in ['a','e','i','o','u'] else 'A ') 
                objText += obj.name + ' (' + obj.id + ')'
                objOut.append(objText)
        prnt(objOut)

    if len(state.room.exits):
        print('')
        exitOut = ["Exits:"]
        for exit in state.room.exits:
            exitOut.append('- ' + exit)
        prnt(exitOut)

def inventory():
    if len(state.inventory):
        output = []
        for item in state.inventory:
            output.append('')
            output.append('- ' + item.name + ' (' + item.id + '): ')
            output.append('  ' + item.desc)
        prnt(output)
    else:
        print('')
        prnt("Your inventory is empty")

def go(cmd):
    global state

    # Get the direction
    direction = cmd[3:]

    # Update coords and determine name for message
    if direction in westDirections:
        dirName = 'west'
        tmpX = state.locX - 1
        tmpY = state.locY
    elif direction in eastDirections:
        dirName = 'east'
        tmpX = state.locX + 1
        tmpY = state.locY
    elif direction in northDirections:
        dirName = 'north'
        tmpX = state.locX
        tmpY = state.locY + 1
    elif direction in southDirections:
        dirName = 'south'
        tmpX = state.locX
        tmpY = state.locY - 1

    # Try to get the room
    tmpRoom = getRoom(tmpX,tmpY)
        
    # Room found
    if tmpRoom.name != '':
        roomKey = tmpRoom.key.split('|')
        if len(roomKey) == 2 and not inInventory(roomKey[0]):
            prnt('The exit is locked. You need "' + roomKey[1]+ '"')
        else:
            state.locX = tmpX
            state.locY = tmpY
            updateLoc(tmpX,tmpY)
            state.room = tmpRoom
            prnt('You go ' + dirName)
            prnt('Current location: ' + state.room.name + ' (' + str(state.locX) + ',' + str(state.locY) + ')')
    # No room found
    else:
        prnt('There is no exit in that direction')

def teleport(cmd):
    global state

    # Get the coords
    tmpCoords = cmd[9:].split(' ')
    tmpX = int(tmpCoords[0])
    tmpY = int(tmpCoords[1])
    if len(tmpCoords) == 2:
        # Try to get the room
        tmpRoom = getRoom(tmpX, tmpY)
        
        # Room found
        if tmpRoom.name != '':
            state.room = tmpRoom
            state.locX = tmpX
            state.locY = tmpY
            updateLoc(state.locX,state.locY)
            prnt('You teleported to ' + str(state.locX) + ',' + str(state.locY))
            prnt('Current location: ' + state.room.name + ' (' + str(state.locX) + ',' + str(state.locY) + ')')
        # No room found
        else:
            prnt('There is no room at that location')

def objCmd(cmd):
    sp = cmd.split(' ')
    # Look for object commands
    found = False
    if len(state.room.objects) and len(sp) > 1:
        for obj in state.room.objects:
            if obj.id == sp[1]:
                for act in obj.actions:
                    if sp[0] in act.triggers:
                        found = True
                        inIf = False
                        inElse = False
                        for i in act.instructions:
                            if i.startswith('IF'):
                                ifTrue = False
                                inIf = True
                                condition = i[3:].split('=')
                                if condition[0] == 'INVENTORY':
                                    keys = condition[1].split(',')
                                    ifTrue = True
                                    for key in keys:
                                        if not inInventory(key):
                                            ifTrue = False
                                else:
                                    propFileName = getPropFileName(state.room.user, state.room.x, state.room.y, obj, condition[0])
                                    propFile = open(propFileName,'r')
                                    if propFile.read().strip() == condition[1]:
                                        ifTrue = True
                                    propFile.close()
                            if i.startswith('ELSE') and inIf:
                                inElse = True
                            elif i == 'ENDIF':
                                inIf = False
                                inElse = False
                            else:
                                runCmd = True
                                if inIf and not inElse and not ifTrue:
                                    runCmd = False
                                elif inElse and ifTrue:
                                    runCmd = False
                                if runCmd:
                                    if i.startswith('ECHO'):
                                        prnt(i[5:])
                                    elif i.startswith('GRAB'):
                                        for obj in state.room.objects:
                                            if obj.id == i[5:]:
                                                addToInventory(obj)
                                    elif i.startswith('SET'):
                                        info = i[4:].split('=')
                                        propFileName = getPropFileName(state.room.user, state.room.x, state.room.y, obj, info[0])
                                        propFile = open(propFileName,'w')
                                        propFile.write(info[1])
                                        propFile.close()

                                        for prop in obj.props:
                                            if prop.key == info[0]:
                                                prop.value = info[1]
                        break
    if not found:
        prnt('Command not found')


if not os.path.exists(configPath):
    print('')
    print('Welcome traveller! It appears you are new here. I can help you get set up.')
    print('')

    # Ask some questions
    name = input('[?] What is your character\'s name? ')
    desc = input('[?] Describe your character: ')

    # Create new .world dir in the home dir
    if not os.path.exists(rootDir):
        os.makedirs(rootDir)

    # Create the config file
    configFile = open(configPath,'w')
    configFile.write('name=' + name + '\n')
    configFile.write('desc=' + desc + '\n')
    configFile.close()

    # Create loc file
    if not os.path.exists(locPath):
        locFile = open(locPath,'w')
        locFile.write('0,0')
        locFile.close()

    # Create inventory file
    if not os.path.exists(inventoryPath):
        locFile = open(inventoryPath,'w')
        locFile.close()

    # Create rooms dir
    if not os.path.exists(roomsPath):
        os.makedirs(roomsPath)

    # Create state dir
    if not os.path.exists(statePath):
        os.makedirs(statePath)

# Find current room
locFile = open(locPath,'r')
coords = locFile.read().strip().split(',')
locFile.close()
state = State()
state.locX = int(coords[0])
state.locY = int(coords[1])
state.room = getRoom(state.locX, state.locY)

# Load inventory
state.inventory = getInventory()

print('')
print('> Welcome to ~world!')
prnt('Current location: ' + state.room.name + ' (' + str(state.locX) + ',' + str(state.locY) + ')')
print('')

# Keep the program active
active = True
while active == True:

    # Display a prompt
    cmd = input('> ')

    # CMD: look (object)
    if cmd.startswith('look ') and len(cmd) > 5: lookObj(cmd)
    # CMD: grab (object)
    elif cmd.startswith('grab ') and len(cmd) > 5: grabObj(cmd)
    # CMD: drop (object)
    elif cmd.startswith('drop ') and len(cmd) > 5: dropObj(cmd)
    # CMD: look
    elif cmd == 'look': look()
    # CMD: inventory
    elif cmd == 'inventory': inventory()
    # CMD: go
    elif cmd.startswith('go ') and cmd[3:] in validDirections: go(cmd)
    # CMD: teleport
    elif cmd.startswith('teleport'): teleport(cmd) 
    # CMD: quit
    elif cmd == 'quit' or cmd == 'exit': active = False
    # CMD: obj commands
    else: objCmd(cmd)

    print('')

