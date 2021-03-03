#!/usr/bin/env python3
import os

output = '<html><head><style type="text/css">a{color:#00aaee;text-decoration:none;}span,a { display: inline-block; width: 20px; height: 20px; overflow:hidden; text-align: center; }body{background:#2c2c2c;color:#555;font-size: 20px;font-family:monospace;}</style></head><body>'

users = os.listdir('/home')
foundRooms = []
lowestX = 0
lowestY = 0
highestX = 0
highestY = 0
for u in users:
    worldPath = '/home/' + u + '/.world'
    if os.path.exists(worldPath):
        rooms = os.listdir(worldPath + '/rooms')
        for room in rooms:
            if "." not in room:
                coords = room.replace('n','-').split('_')
                x = int(coords[0])
                y = int(coords[1])

                roomData = [u]
                roomData.append(x)
                roomData.append(y)

                roomPath = worldPath + '/rooms/' + room
                roomFile = open(roomPath, 'r')
                roomLines = [x.strip('\n') for x in roomFile]
                roomFile.close()
                
                rFile = open('/home/dustin/public_html/world/' + room + '.html','w')

                rFile.write('<html><head><style type="text/css">a{color:#00aaee;text-decoration:none;}body{background:#2c2c2c;color:#fff;font-family:monospace;}</style></head><body><pre>')

                rFile.write('[' + coords[0] + ',' + coords[1] + ']<br><br>')

                for line in roomLines:
                    rFile.write(line + '<br>')
                    if line.startswith('NAME'):
                        roomData.append(line[7:])

                rFile.write('</pre></body></html>')
                rFile.close()

                roomData.append(room)

                foundRooms.append(roomData)

                if highestX < x: highestX = x
                if lowestX > x: lowestX = x
                if highestY < y: highestY = y
                if lowestY > y: lowestY = y

for y in range(lowestY-1,highestY+2):
    for x in range(lowestX-1,highestX+2):
        found = False
        r = []
        for room in foundRooms:
            if room[1] == x and room[2] == y:
                found = True
                r = room
        if found:
            output += '<a href="' + r[4] + '.html" title="' + '[' + str(x) + ',' + str(y) + '] [~' + r[0] + '] ' + r[3] + '">#</a>'
        else:
            output += '<span title="' + '[' + str(x) + ',' + str(y) + ']">.</span>'
    output += '<br>'

output += '</body></html>'

iFile = open('/home/dustin/public_html/world/index.html','w')
iFile.write(output)
rFile.close()
