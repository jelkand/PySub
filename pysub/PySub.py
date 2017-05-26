"""This module defines a simple submarine in python"""
import random
import sys
import server_message
import socket_manager
from util import Coordinate, Direction, Equipment
from submarine import Submarine


DEFAULT_USERNAME = "PySub"
DEFAULT_SERVER_ADDRESS = "localhost"
#DEFAULT_SERVER_ADDRESS = "127.0.0.1"
DEFAULT_SERVER_PORT = 9555
ALL_DIRECTIONS = [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]


class PySub():
    """This is a sample skeleton sub in python"""
    verbose = False
    socket_manager = None
    game_map = dict()
    spotted = list()
    detonations = list()
    torpedo_hits = list()
    mine_hits = list()
    my_sub = Submarine(0)
    random_destination = None
    map_width = 0
    map_height = 0
    turn_number = 0

    def __init__(self, username, server_address, server_port, verbose):
        self.username = username
        self.server_address = server_address
        self.server_port = server_port
        self.verbose = verbose
        self.socket_manager = socket_manager.SocketManager(server_address, server_port, verbose)

    def login(self):
        """Logs in to server"""
        self.socket_manager.connect()
        self.configure(server_message.GameConfigMessage(self.socket_manager.receive_message(), self.socket_manager))

        self.my_sub.location = self.random_square(None)
        self.socket_manager.send_message("J|{0}|{1}|{2}".format(self.username, self.my_sub.get_x(), self.my_sub.get_y()))

        response = self.socket_manager.receive_message()
        if response != "J|{0}".format(self.username):
            raise IOError("Failed to join. Server response: {0}".format(response))


    def configure(self, message):
        """Configures the game"""
        self.turn_number = 0
        self.map_width = message.map_width
        self.map_height = message.map_height
        self.my_sub = Submarine(0)

        #initialize game map
        for y_val in range(1, self.map_height):
            for x_val in range(1, self.map_width):
                coord = Coordinate(x_val, y_val)
                self.game_map[coord] = coord

        print("Joining as player:   {0}".format(self.username))
        print("Server Host:Port:    {0}:{1}".format(self.server_address, self.server_port))
        print("Server Version:      {0}".format(message.server_version))
        print("Game Title:          {0}".format(message.game_title))
        print("Game Map Size:       {0}x{1}".format(self.map_width, self.map_height))

        for setting in message.custom_settings:
            print("Customized Setting:      {0}".format(setting))
            if setting.setting_name == "SubsPerPlayer":
                raise ValueError("More than one sub per player is not currently supported")
            elif setting.setting_name == "Obstacle":
                coord = Coordinate(setting.values[0], setting.values[1])
                self.game_map[coord].blocked = True

    def play(self):
        """Receives and handles messages"""
        message = self.socket_manager.receive_message()
        while message is not None:
            if message.startswith("B"): #Begin Turn
                self.handle_begin_turn_message(server_message.BeginTurnMessage(message))
            elif message.startswith("S|"): #Sonar Detection
                self.handle_sonar_detection_message(server_message.SonarDetectionMessage(message))
            elif message.startswith("D|"): #Detonation
                self.handle_detonation_message(server_message.DetonationMessage(message))
            elif message.startswith("T|"): #Torpedo Hit
                self.handle_torpedo_hit_message(server_message.TorpedoHitMessage(message))
            elif message.startswith("O|"): #Discovered object
                self.handle_discovered_object_message(server_message.DiscoveredObjectMessage(message))
            elif message.startswith("I|"): #Sub info
                self.handle_info_message(server_message.SubmarineInfoMessage(message))
            elif message.startswith("H|"): #player score
                self.handle_player_score_message(server_message.PlayerScoreMessage(message))
            elif message.startswith("F|"): #game finished
                self.handle_game_finished_message(server_message.GameFinishedMessage(message, self.socket_manager))
                break
            else:
                print("error in message: {0}".format(message))
            message = self.socket_manager.receive_message()

    def check_turn_number(self, message):
        """Validates that the turn number matches the received turn number"""
        if message.turn_number is not self.turn_number:
            raise RuntimeError("Expected turn number: {0} does not match message turn number {1}" \
            .format(self.turn_number, message.turn_number))


    def handle_begin_turn_message(self, message):
        """Handles a begin turn message"""
        self.turn_number = message.get_part(1)
        if self.verbose:
            #TODO
            pass
        self.issue_command(self.my_sub) #logic goes here

        #Clear all info so it can be repopulated by turn results method.
        for entry in self.game_map:
            entry.reset()
        self.spotted = list()
        self.detonations = list()
        self.torpedo_hits = list()

    def handle_sonar_detection_message(self, message):
        """handles sonar detection message"""
        self.check_turn_number(message)
        self.spotted.append(message)

    def handle_detonation_message(self, message):
        """handles detonation message"""
        self.check_turn_number(message)
        self.detonations.append(message)

    def handle_torpedo_hit_message(self, message):
        """handles torpedo hit message"""
        self.check_turn_number(message)
        self.torpedo_hits.append(message)

    def handle_discovered_object_message(self, message):
        """handles discovered object message"""
        self.check_turn_number(message)
        square = self.game_map[message.location]
        if square and not square.blocked:
            square.object_size += message.size
            square.foreign_object_size += message.size

    def handle_info_message(self, message):
        """handles sub info messages"""
        self.check_turn_number(message)
        self.my_sub.update(message)
        self.game_map[self.my_sub.location].foreign_object_size -= self.my_sub.size

    def handle_player_score_message(self, message):
        """handles player score message"""
        self.check_turn_number(message)

    def handle_game_finished_message(self, message):
        """handles game finished message"""
        print("Game finished")
        for result in message.player_results:
            print("    {0} score: {1}".format(result.player_name, result.player_score))

    def issue_command(self, sub):
        """Fancy AI logic for the sub. Lifted wholesale from Dudly Jr"""

        #shoot things if possible
        target = self.get_torpedo_target(sub)
        if target is not None:
            self.socket_manager.send_message(sub.fire_torpedo(self.turn_number, target))
            self.random_destination = None
            return

        #maybe ping
        if sub.max_sonar_charge or (not self.spotted and sub.torpedo_range >= sub.sonar_range) and sub.sonar_range > 1 + random.randint(0, 6):
            self.socket_manager.send_message(sub.ping(self.turn_number))
            self.random_destination = None
            return

        #maybe new destination
        if self.random_destination is None or self.random_destination == sub.location:
            self.random_destination = self.random_square(sub.location)
            if self.verbose:
                print("New random destination: {0}".format(self.random_destination))

        charge = Equipment.SONAR if sub.max_torpedo_charge or sub.torpedo_range >= sub.sonar_range or random.randint(0, 100) < 33 else Equipment.TORPEDO
        direction = self.get_direction_toward(sub.location, self.random_destination)
        self.socket_manager.send_message(sub.move(self.turn_number, direction, charge))

    def get_direction_toward(self, start, destination):
        """Gets the direction to get from location to destination"""
        if start == destination or not self.game_map[start] or not self.game_map[destination]:
            raise ValueError("Invalid direction coordinates {0} - {1}".format(start, destination))

        directions = list()

        if destination.x < start.x:
            directions.append(Direction.WEST)
        if destination.x > start.x:
            directions.append(Direction.EAST)
        if destination.y < start.y:
            directions.append(Direction.NORTH)
        if destination.y > start.y:
            directions.append(Direction.SOUTH)

        direction = random.choice(directions)
        if self.game_map[start.shifted(direction)] and not self.game_map[start.shifted(direction)].blocked:
            return direction

        directions.extend(ALL_DIRECTIONS)
        random.shuffle(directions)
        for rand_direction in directions:
            if self.game_map[start.shifted(direction)] and not self.game_map[start.shifted(rand_direction)].blocked:
                return rand_direction

        #in theory unreachable
        raise ValueError("yo you can't move anywhere from {0}".format(start))

    def get_torpedo_target(self, sub):
        """Get a target to shoot"""
        if sub.torpedo_range < 2:
            return

        largest_size = 1
        targets = list()
        in_range = self.squares_in_range_of(sub.location, sub.torpedo_range)
        for coord in in_range:
            if self.get_blast_distance(sub.location, coord) > 1:
                square = self.game_map[coord]
                if square.foreign_object_size >= largest_size and square.foreign_object_size == square.object_size:
                    targets.append(coord)

        if not targets:
            return

        return random.choice(targets)

    def get_blast_distance(self, from_coord, to_coord):
        """returns a blast distance"""
        if not self.game_map[from_coord] or not self.game_map[to_coord]:
            raise ValueError("get blast distance fed invalid coords")
        x_diff = abs(from_coord.x - to_coord.x)
        y_diff = abs(from_coord.y - to_coord.y)
        return max(x_diff, y_diff)

    def squares_in_range_of(self, location, torpedo_range):
        """Finds all squares in range of the provided location"""
        if not self.game_map[location]:
            raise ValueError("location {0} is invalid".format(location))
        destinations = dict()
        if range > 0:
            self.add_destinations(destinations, location, 1, torpedo_range)
        return destinations

    def add_destinations(self, input_destinations, coord, distance, torpedo_range):
        """recursively finds all valid destinations from squares"""
        next_potential_destinations = list()
        for direction in ALL_DIRECTIONS:
            temp_destination = coord.shifted(direction)
            if self.game_map[temp_destination] and not self.game_map[temp_destination].blocked:
                previous_distance = input_destinations[temp_destination]
                if not previous_distance or distance < previous_distance:
                    input_destinations[temp_destination] = distance
                    if not self.game_map[temp_destination]:
                        next_potential_destinations.append(temp_destination)

        if distance < torpedo_range:
            for potential in next_potential_destinations:
                self.add_destinations(input_destinations, potential, distance + 1, torpedo_range)


    def random_square(self, location):
        """Get a random square on the map"""
        while True:
            x_val = random.randint(1, self.map_width)
            y_val = random.randint(1, self.map_height)
            location = Coordinate(x_val, y_val)
            if self.game_map[location] and not self.game_map[location].blocked:
                return location

if __name__ == '__main__':
    if '--help' in sys.argv or '-h' in sys.argv:
        print("Usage will go here")
    verbose = '--verbose' or '-v' in sys.argv

    bot = PySub(DEFAULT_USERNAME, DEFAULT_SERVER_ADDRESS, DEFAULT_SERVER_PORT, verbose)

    try:
        bot.login()
        bot.play()
    except (ValueError, RuntimeError, IOError) as error:
        print("ERROR: {0}".format(error))
    finally:
        bot.socket_manager.disconnect()

