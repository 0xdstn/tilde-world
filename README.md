# Tilde world

Tilde world (~world) is a flat-file, community powered, text adventure game intended to be run on tilde servers.

## Description

Tilde world can be run on tilde.town by running **~dustin/projects/tilde-world/world.py**. When you first run it it will welcome you and ask your character's name and description.

When you finish the setup it will create a **~/.world** directory with some configuration files and a **rooms** directory where you can create your own rooms (see below).

Your name and description is saved in **~/.world/config**.

When the game is looking for a room at a coordinate, it will loop through all of the users on the server and check for that coordinate in their **.world/rooms** directory. The first one found is used, if there are duplicates (try not to step on each other's toes please).

Your current position is saved in **~/.world/loc** in the format **x,y**.

Your inventory is saved in **~/.world/inventory**. Each item goes on one line in the format **key : x,y**. The x,y is the room the object came from so we can reference it's data again.

The state for props are saved in `~/.world/state`. It saves in the format **object_prop.txt**. As props change via user interaction, these files are updated. They are created upon entering a room with an object that has a prop.

## Creating rooms

You can create your own rooms by placing files in the **~/.world/rooms** directory.

The files are named for their coordinates in the format **x_y**. Negative coordinates use an "n" instead of "-". So a room at coordinate **-1 0** would be a file named **n1_0**.

A basic room looks like this:

```
NAME : Landing room
DESC : An ordinary room
```

Rooms have the following properties available:

- `NAME` - The name of the room
- `DESC` - A description of the room. This is displayed with the **look** command
- `KEY` - Optional. An ID and name of an item required to enter this room from any direction in this format: **west-key|West room key**
- `TELEPORT` - Optional. x,y coordinates to redirect the user to if they teleport here (such as the start of a dungeon).

## Objects

A room can contain multiple objects. A room with objects would look like this:

```
NAME : Landing room
DESC : An ordinary room
OBJECTS
  -
    ID : sword
    NAME : wooden sword
    GRAB : true
    DESC : A wooden sword in good condition
  -
    ID : shield
    NAME : wooden shield
    GRAB : true
    DESC : A wooden shield in good condition
```

 Objects have the following properties available:

- `ID` - A unique identifier for referencing the object
- `NAME` - The name of the object
- `DESC` - A description of the object displayed with **look obj_id**. You can reference props with [propkey], and they will automatically be replaced with the value of the prop
- `GRAB` - (Optional, default false) **true** or **false**, if the item can be picked up by a user
- `HIDDEN` - (Optional, default false) **true** or **false**, if the item is listed in the room with the **look** command
- `ACTIONS` - (Optional) A list of actions, see below
- `PROPS` - (optional) A list of props, see below

## Props and actions

Objects can have props and actions.

Props are key/value pairs. They will be stored in a file specific to the room/prop and the user. That means that whatever state a room and it's objects are in for one user does not affect it for another user.

Actions are a list of triggers and a list of instructions.

Here is an object with a prop and an action:

```
  -
    ID : lamp
    NAME : ordinary lamp
    GRAB : false
    DESC : A lamp with a switch. It is currently [power].
    PROPS
      power=off
    ACTIONS
      turn|switch|push|pull
        IF power=on
        SET power=off
        ECHO You turn off the lamp
        ELSE
        SET power=on
        ECHO You turn on the lamp
        ENDIF
```

When the user runs **turn lamp** it will either turn the power prop on or off depending on if it is currently set to on or off.

## Action instructions

Actions currently support the following:

- `IF prop_name=value` - If prop of the item is the provided value, all following instructions until an **ELSE** or **ENDIF** will be run
- `IF INVENTORY=item1,item2` - If the inventory contains the provided item(s), all following instructions until an **ELSE** or **ENDIF** will be run
- `ELSE` - Placed between an **IF** and **ENDIF**. If the IF statement is false, all following instructions until an **ENDIF** will be run
- `ECHO message` - Prints out the provided message
- `GRAB object` - Adds the provided object key to the inventory (must also be in the same room, hidden or not)
- `TELEPORT x y` - Teleports to provided x,y coordinates

## Game commands

As a user of the game you can run the following commands:

- `look` - View the room along with it's objects and exits
- `look [object]` - View the provided object and it's actions
- `grab [object]` - Add the provided object to the inventory
- `drop [object]` - Remove the provided object from the inventory
- `[action] [object]` - Runs the provided action on the provided object
- `inventory` - List the inventory
- `go [direction]` - Go the provided direction (north, south, east, west)
- `teleport [x] [y]` - Go to the provided coordinates
- `quit` - Quit ~world
- `help` - Displays the help menu
- `about` - Displays information about the author and project

## Future plans

- Add more action logic

## Release notes

- `v1.1.1` Added TELEPORT prop to rooms  to provide x,y coordinates to redirect the user to if they teleport to the room (such as the start of a dungeon)
- `v1.1.0` Changed inventory system so you can use item actions after grabbing them
- `v1.0.2` Added TELEPORT action instruction
- `v1.0.1` Added help and about commands
- `v1.0.0` Initial release with base functionality
