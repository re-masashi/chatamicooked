import os, sys, time, random, threading
from collections import namedtuple

import hangman

# utility functions


def clear(): return os.system('setterm -reset' if os.name == 'nt' else 'tput reset')
clear()

def decrease_hunger(player):
	while True:  # Keep running until the game ends
		time.sleep(10)  # Wait for 10 seconds

		if player.hunger >= 10:
			if player.health<=1:
				print("You starved to death. ")
				sys.exit(0)
			player.health -= 1
		else:
			player.hunger += 1

# Game Data Structures

Room = namedtuple("Room", ["name", "description", "exits", "items"])

rooms = {
}
WINDOW_WIDTH = 60
WINDOW_HEIGHT = 13  # must always be odd


class Player:

    def __init__(self):
        self.inventory = [
            "apple",
            "water"
        ]
        self.visited_rooms = []
        self.hunger = 6
        self.health = 9
        self.position = [0, 0]
        self.message = rooms["lobby"].description
        self.current_room = "lobby"
        self.has_used_key = False

    def move(self, direction):
        current_room = rooms[self.current_room]
        if self.current_room not in self.visited_rooms:
            self.visited_rooms += [self.current_room]

        if direction in current_room.exits:
            self.current_room = current_room.exits[direction]
            self.message = f"Moved to {rooms[self.current_room].name}\n{rooms[self.current_room].description}"
        else:
            self.message = "You can't go that way. No exits are present there."

    def display(self, tutorial=False):
        current_room = rooms[self.current_room]

        map_width = WINDOW_WIDTH - 4  # Leave space for borders
        # Leave space for room name, description, stats, etc.
        map_height = WINDOW_HEIGHT - 7

        map_display = [[" " for _ in range(map_width)]
                       for _ in range(map_height)]

        # Calculate player position on map (center)
        player_x = map_width // 2
        player_y = map_height // 2
        map_display[player_y][player_x] = "O"  # Player character

        for direction, dest_room in current_room.exits.items():
            if direction == "north":
                map_display[0][player_x:player_x+6] = "|exit|"
            elif direction == "south":
                map_display[map_height - 1][player_x:player_x+6] = "|exit|"
            elif direction == "east":
                map_display[player_y][map_width-5:map_width] = "|exit"
            elif direction == "west":
                map_display[player_y][:5] = "exit|"

        print(
            f"{"="*int(WINDOW_WIDTH/2)} {"room: "+rooms[self.current_room].name} {"="*int(WINDOW_WIDTH/2-len("room: "+rooms[self.current_room].name)-2)}"
        )
        for row in map_display:
            print("| " + "".join(row) + " |")  # Add side borders

        print("-" * WINDOW_WIDTH)  # bottom border

        items = "| ".join(self.inventory)
        if len(items) > 28:
            items = items[:25]+"..."
        
        if self.hunger >= 10:
        	stats = f"starving[hunger: {self.hunger}|heath: {self.health}]"

        stats = f"[hunger: {self.hunger}|heath: {self.health}]"

        print(f"{items}{" "*(WINDOW_WIDTH-len(items)-len(stats))}{stats}")
        print()

        if tutorial:
            for char in self.message:
                print(char, end="", flush=True)
                (time.sleep(0.05) if char == '.' else time.sleep(0.01))
            print()
            return

        if self.current_room not in self.visited_rooms:
            for char in self.message:
                print(char, end="", flush=True)
                (time.sleep(0.05) if char == '.' else time.sleep(0.01))
            print()
        else:
            print(self.message)

        self.message = ""


def generate_map():
    rooms = {}
    # Possible exit directions
    directions = ["north", "south", "east", "west"]

    # Start with the lobby
    rooms["lobby"] = Room("Lobby", "A grand lobby.", {}, ["water"])

    # Generate connecting rooms
    current_room = "lobby"
    path_to_kitchen = []  # Keep track of rooms leading to kitchen
    for _ in range(2):  # only two rooms between lobby and kitchen
        # Choose a random direction for exit from current room
        available_directions = [
            dir for dir in directions if dir not in rooms[current_room].exits]
        if not available_directions:
            break  # No more directions for the current room
        direction = random.choice(available_directions)

        new_room_name = generate_room_name(set(rooms.keys()))
        rooms[new_room_name] = Room(new_room_name.replace(
            "_", " ").title(), generate_description(), {}, generate_items())

        # Connect the new room to the current room using chosen direction and opposite_direction
        opposite_direction = {
            "north": "south", "south": "north", "east": "west", "west": "east"}[direction]
        rooms[current_room].exits[direction] = new_room_name
        rooms[new_room_name].exits[opposite_direction] = current_room

        path_to_kitchen.append(new_room_name)
        current_room = new_room_name

    # Place the kitchen
    rooms["old_kitchen"] = Room(
        "Old Kitchen", "A spooky old kitchen.", {}, ["key"])

    # Always connect the last generated room to the kitchen and the kitchen to the secret tunnel.
    last_room = path_to_kitchen[-1]
    available_directions = [
        dir for dir in directions if dir not in rooms[last_room].exits]
    if available_directions:  # Check for available directions
        direction = random.choice(available_directions)
        opposite_direction = {
            "north": "south", "south": "north", "east": "west", "west": "east"}[direction]
        rooms[last_room].exits[direction] = "old_kitchen"
        rooms["old_kitchen"].exits[opposite_direction] = last_room

    rooms["old_kitchen"].exits["east"] = "secret_tunnel"
    rooms["secret_tunnel"] = Room("Secret Tunnel", "A dark tunnel.", {"west": "old_kitchen", "east": "malbolge"}, [])
    rooms["malbolge"] = Room("Malbolge", "The Eighth circle of hell.", {"west": "secret_tunnel"}, [])

    return rooms


def generate_connected_room(rooms, current_room, directions):
    exits = random.sample(directions, random.randint(1, 3)
                          )  # generate 1 to 3 exits
    room_names = set(rooms.keys())

    map_width = WINDOW_WIDTH - 4  # Leave space for borders
    # Leave space for room name, description, stats, etc.
    map_height = WINDOW_HEIGHT - 7

    for dx, dy, direction, opposite_direction in exits:
        current_x, current_y = rooms[current_room].x + \
            dx, rooms[current_room].y+dy
        new_room_name = generate_room_name(room_names)
        room_names.add(new_room_name)
        # print("room", new_room_name)

        if new_room_name not in rooms:
            item_positions = []
            items = generate_items()

            player_x = map_width // 2
            player_y = map_height // 2

            rooms[new_room_name] = Room(new_room_name.replace("_", " ").title(), generate_description(),
                                        current_x, current_y, 20, 10, {}, items)
            rooms[current_room].exits[direction] = new_room_name
            rooms[new_room_name].exits[opposite_direction] = current_room

    added_items = []
    if random.random() < 0.25:
        added_items.append("apple")
        rooms[new_room_name].items.append("apple")

    return new_room_name, added_items  # returns generated items


def generate_items():
    possible_items = ["sword", "potion", "map", "compass",
                      "torch", "book", "gems"]
    num_items = random.randint(0, 2)  # Up to 2 items per room
    items = random.sample(possible_items, num_items)
    
    # 25% chances of having an apple
    if random.random() <= 0.25:
        items+=["apple"]

    # 33% chances of having water
    if random.random() <= 0.33:
        items+=["water"]

def generate_room_name(taken_names):
    adjectives = ["grand", "mysterious", "dark", "ancient",
                  "hidden", "forgotten", "eerie", "opulent"]
    nouns = ["hall", "chamber", "room", "corridor",
             "tunnel", "cavern", "sanctuary", "lair"]
    while True:
        name = f"{random.choice(adjectives)}_{random.choice(nouns)}"
        if name not in taken_names:
            return name


def generate_description():
    descriptions = [
        "You are in a dimly lit room.",
        "A strange odour fills the air.",
        "Dust motes dance in the faint light.",
        "You hear a faint dripping sound.",
        "Cobwebs hang from the ceiling."
    ]
    # Adds a random adjective and noun
    return random.choice(descriptions) + add_detail()


def add_detail():
    adjectives = ["grand", "mysterious", "dark", "ancient",
                  "hidden", "forgotten", "eerie", "opulent", "creepy"]
    nouns = ["hall", "chamber", "room", "corridor",
             "tunnel", "cavern", "sanctuary", "lair", "dungeon"]
    return " There is a "+random.choice(adjectives)+" "+random.choice(nouns)+" here."


def game_loop(state):
    player = state['player']
    
    hunger_thread = threading.Thread(target=decrease_hunger, args=(player,), daemon=True)
    hunger_thread.start()

    while True:
        clear()

        if "lobby" not in player.visited_rooms:
            player.visited_rooms += ["lobby"]

        if player.current_room == 'malbolge':

        	if "key" not in player.inventory and player.has_used_key == False:
        	    player.message = "you need to find the key to enter this room! go back to the previous rooms and search for it!!"
        	    player.current_room = "secret_tunnel"
        	    continue

        	if player.has_used_key == False:
        		player.message = "you need to use the key in the tunnel to this room!"
        		player.current_room = "secret_tunnel"
        		continue

        	print("welcome to Malbolge. the Eighth circle of hell. win this game to free the innocent soulds trapped here.")
        	if hangman.game_loop(None):
        	    print("you have freed them! they all want to thank you!")
        	    print("please play again")
        	    return
        	else:
        	    print("game over")

        player.display()

        try:
            command = input("command > ")
        except (KeyboardInterrupt, EOFError):  # Handle Ctrl+C and Ctrl+D
            print("\nGoodbye!")
            sys.exit(0)

        if not command:
            continue

        args = command.split()

        if args[0] == 'move':
            if len(args) == 2:
                player.move(args[1])
            else:
                # clear error message
                player.message = "Usage: move <direction>"

        elif args[0] == 'look':
            # add look command
            player.message = rooms[player.current_room].description
        elif args[0] == 'search':
            if len(rooms[player.current_room].items) == 0:
                player.message = "no items found"
            elif len(rooms[player.current_room].items) == 1:
                player.message = "found a " + \
                    rooms[player.current_room].items[0]
            else:
                player.message = "found the following items: " + ",".join(
                    rooms[player.current_room].items)
        elif args[0] == 'pick':
            if len(args) == 2:
                if args[1].lower() in rooms[player.current_room].items:
                    player.inventory += [args[1].lower()]
                    rooms[player.current_room].items.remove(args[1].lower())
                    player.message = "picked up a "+args[1]
                else:
                    player.message = "no such item exists in this room!"
            else:
                player.message = "Usage: pick <item>"
        elif args[0] == 'use':
            if len(args) == 2:
                if args[1].lower() in player.inventory:

                    if args[1].lower()=='key' and (player.current_room != 'secret_tunnel'):
                    	player.message = "cannot use the key here"
                    	continue
                    if args[1].lower()=='key' and (player.current_room == 'secret_tunnel'):
                    	player.message = "key used..."
                    	player.has_used_key = True
                    if args[1].lower()=='apple':
                    	player.hunger -= 5
                    	player.health += 5
                    if args[1].lower()=='water':
                   		player.health += 10
                    if args[1].lower()=='potion':
                   		player.hunger -= 2
                   		player.health += 4

                    player.inventory.remove(args[1].lower())
                    player.message = "used a "+args[1]
                else:
                    player.message = "no such item exists in your inventory!"
            else:
                player.message = "Usage: use <item>"
        elif args[0] == 'quit':
            print("Goodbye!")
            sys.exit(0)
        elif args[0] == 'debug':
            print("visited_rooms: ", player.visited_rooms)
            print("current_room: ", player.current_room)
            print("message: ", player.message)
            input()
        # ... Add more commands (inventory, get, drop, use, etc.)
        else:
            print("Invalid command.")


if __name__ == '__main__':
    rooms = generate_map()
    state = {}
    state["state"] = "idle"
    state["player"] = Player()
    state["player"].current_room = list(rooms.keys())[0]
    state['player'].message = """
welcome to hotel gleam lob's lobby!
that circle in there is you.
you can see exits in maybe the north, south, east or west.

the possible commands are:
- move <direction>: to move the exit on <direction>
- look: to make your player look around and describe the surroundings
- search: to search the room for items
- pick <item>: picks up the mentioned item if it is present in the room

if you see a single letter in the map, it is the first letter of an item.

hope you enjoy the game!
"""

    state['player'].display(tutorial=True)
    state['player'].message = rooms["lobby"].description
    input(">")
    game_loop(state)
