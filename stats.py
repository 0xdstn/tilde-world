#!/usr/bin/env python3

import os

users = os.listdir('/home')

for u in users:

    worldPath = '/home/' + u + '/.world'

    if os.path.exists(worldPath):

        print('')
        print('[*] ' + u)

        locFile = open(worldPath + '/loc','r')
        for line in [x.strip('\n') for x in locFile]:
            print('    [LC] ' + line)
        locFile.close()

        configFile = open(worldPath + '/config','r')
        for line in [x.strip('\n') for x in configFile]:
            print('    [CF] ' + line.replace('=',': '))
        configFile.close()

        inventoryFile = open(worldPath + '/inventory','r')
        for line in [x.strip('\n') for x in inventoryFile]:
            print('    [IN] ' + line.split(' : ')[0])
        inventoryFile.close()

        rooms = os.listdir(worldPath + '/rooms')
        for room in rooms:
            if "." not in room:
                print('    [RM] ' + room.replace('n','-').replace('_',','))
