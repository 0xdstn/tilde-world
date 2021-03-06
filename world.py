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
        self.teleport = ''

    def setItem(self, key, val):
        if key == 'name': self.name = val
        elif key == 'key': self.key = val
        elif key == 'desc': self.desc = val
        elif key == 'objects': self.objects = val
        elif key == 'teleport': self.teleport = val

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

def getPropFileName(obj, prop):
    propFileName = statePath
    propFileName += obj.id.replace(' ','-') + '_' 
    propFileName += prop + '.txt'

    return propFileName

def getInventory():
    inventory = []
    inventoryFile = open(inventoryPath,'r')
    inventoryLines = [x.strip('\n') for x in inventoryFile]
    inventoryFile.close()
    for line in inventoryLines:
        info = line.split(' : ')
        if len(info) == 2:
            coords = info[1].split(',')
            if len(coords) == 2:
                tmpRoom = getRoom(int(coords[0]),int(coords[1]))
                for obj in tmpRoom.objects:
                    if obj.id == info[0]:
                        inventory.append(obj)
                        break
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
            roomData = open(roomPath, 'r')
            roomLines = [x.strip('\n') for x in roomData]
            curObj = Object()
            curProp = Prop()
            curAction = Action()
            inProp = False
            inAction = False
            for line in roomLines:
                if line.strip() == '':
                    continue
                if line[0] != ' ':
                    inProp = False
                    inAction = False
                    pieces = line.split(' : ')
                    if len(pieces) == 2:
                        room.setItem(pieces[0].lower(),pieces[1])
                else:
                    if line == '  -':
                        if inProp:
                            curObj.props.append(curProp)
                            inProp = False
                        if inAction:
                            curObj.actions.append(curAction)
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
                        curProp = Prop()
                    elif line.startswith('    ACTIONS'):
                        if inProp:
                            curObj.props.append(curProp)
                            inProp = False
                        inAction = True
                        curAction = Action()
                    elif inProp:
                        pieces = line.strip().split('=')
                        propFileName = getPropFileName(curObj, pieces[0])

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
            tmpY = y - 1
            northPath = roomsPath.replace(username,u) + str(tmpX).replace('-','n') + '_' + str(tmpY).replace('-','n')
            if os.path.exists(northPath):
                room.exits.append('north')
        
        if 'south' not in room.exits:
            tmpX = x
            tmpY = y + 1
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
    for obj in state.inventory:
        if obj.id == key:
            found = True
    return found

def addToInventory(obj,x,y):
    global state

    owned = inInventory(obj.id)

    if owned:
        prnt('You already have one of these')
    else:
        inventoryFile = open(inventoryPath,'a')
        inventoryFile.write(obj.id + ' : ' + str(x) + ',' + str(y) + "\n")
        inventoryFile.close()
        state.inventory.append(obj)
        prnt('You obtain "' + obj.name + '"')

def removeFromInventory(key):
    global state
    
    owned = inInventory(key)

    if not owned:
        prnt('This item is not in your inventory')
    else:
        inventoryFile = open(inventoryPath,'r')
        inventoryLines = [x for x in inventoryFile]
        inventoryFile.close()
        inventoryFile = open(inventoryPath,'w')
        for line in inventoryLines:
            if line.startswith(key + ' :'):
                for obj in state.inventory:
                    if obj.id == key:
                        state.inventory.remove(obj)  
                        prnt('You drop "' + obj.name + '"')
            else:
                inventoryFile.write(line)
        inventoryFile.close()

def lookObj(cmd):
    item = cmd[5:]
    found = False
    objects = getAllObjects()
    for obj in objects:
        if item == obj.id:
            found = True
            desc = obj.desc
            if len(obj.props):
                for prop in obj.props:
                    desc = desc.replace('[' + prop.key + ']', prop.value)
            prnt(desc)
            if len(obj.actions) or obj.grab:
                actionsOut = ['You can:']
                if obj.grab and not inInventory(obj.id):
                    actionsOut.append('- grab')
                for actn in obj.actions:
                    actionsOut.append('- ' + actn.triggers[0])
                if len(actionsOut) > 1:
                    print('')
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
                addToInventory(obj,state.locX,state.locY)
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
        print('')
        for obj in state.inventory:
            output.append('- ' + obj.name + ' (' + obj.id + ')')
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
        tmpY = state.locY - 1
    elif direction in southDirections:
        dirName = 'south'
        tmpX = state.locX
        tmpY = state.locY + 1

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

def moveTo(x,y):
    # Try to get the room
    tmpRoom = getRoom(x,y)
    
    # Room found
    if tmpRoom.name != '':
        state.room = tmpRoom
        state.locX = x
        state.locY = y
        updateLoc(state.locX,state.locY)
        prnt('Current location: ' + state.room.name + ' (' + str(state.locX) + ',' + str(state.locY) + ')')
    # No room found
    else:
        prnt('There is no room at that location')

def teleport(cmd):
    global state

    # Get the coords
    tmpCoords = cmd[9:].split(' ')
    tmpX = int(tmpCoords[0])
    tmpY = int(tmpCoords[1])
    if len(tmpCoords) == 2:
        moveTo(tmpX,tmpY)
        if len(state.room.teleport):
            telCoords = state.room.teleport.split(',')
            if len(telCoords) == 2:
                prnt('Being redirected to dungeon start..')
                moveTo(int(telCoords[0]),int(telCoords[1]))

def getAllObjects():
    objects = []
    ids = []
    for obj in state.room.objects + state.inventory:
        if obj.id not in ids:
            objects.append(obj)
            ids.append(obj.id)
    return objects

def updateProp(obj,key,value):
    propFileName = getPropFileName(obj, key)
    propFile = open(propFileName,'w')
    propFile.write(value)
    propFile.close()

    for prop in obj.props:
        if prop.key == key:
            prop.value = value

def objCmd(cmd):
    sp = cmd.split(' ')
    # Look for object commands
    found = False
    objects = getAllObjects()
    if len(objects) and len(sp) > 1:
        for obj in objects:
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
                                    propFileName = getPropFileName(obj, condition[0])
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
                                        message = i[5:]
                                        if len(obj.props):
                                            for prop in obj.props:
                                                message = message.replace('[' + prop.key + ']', prop.value)
                                        prnt(message)
                                    elif i.startswith('PROMPT'):
                                        info = i[7:].split('|')
                                        if len(info) == 2:
                                            prnt(info[1])
                                            resp = input('  > ').strip()
                                            updateProp(obj,info[0],resp)
                                    elif i.startswith('TELEPORT'):
                                        coords = i[9:].split(' ')
                                        if len(coords) == 2:
                                            moveTo(int(coords[0]),int(coords[1]))
                                    elif i.startswith('GRAB'):
                                        for obj in state.room.objects:
                                            if obj.id == i[5:]:
                                                addToInventory(obj,state.locX,state.locY)
                                    elif i.startswith('SET'):
                                        info = i[4:].split('=')
                                        updateProp(obj,info[0],info[1])
                        break
    if not found:
        prnt('Command not found')

def help():
    prnt('Commands:')
    print('')
    prnt('look               View the room along with it\'s objects and exits')
    prnt('look [object]      View the provided object and it\'s actions')
    prnt('grab [object]      Add the provided object to the inventory')
    prnt('drop [object]      Remove the provided object from the inventory')
    prnt('[action] [object]  Runs the provided action on the provided object')
    prnt('inventory          List the inventory')
    prnt('go [direction]     Go to the provided direction (north, south, east west)')
    prnt('teleport [x] [y]   Go to the provided coordinates')
    prnt('quit               Quit ~world')
    prnt('help               Displays this menu')
    prnt('about              Displays information about the author and project')

def about():
    prnt('Version:      1.1.2')
    prnt('Author:       ~dustin')
    prnt('Source:       https://github.com/0xdstn/tilde-world')
    prnt('More info:    https://tilde.town/~dustin/projects/tilde-world')

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
    cmd = input('> ').strip()

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
    # CMD: help 
    elif cmd == 'help': help()
    # CMD: help 
    elif cmd == 'about': about()
    # CMD: quit
    elif cmd == 'quit' or cmd == 'exit': active = False
    # CMD: obj commands
    else: objCmd(cmd)

    print('')

