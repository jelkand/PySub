"""This module defines a simple submarine in python"""
import ServerMessage
import SocketManager
from Util import Coordinate, Direction, Equipment
from Submarine import Submarine


DEFAULT_USERNAME = "PySub"
DEFAULT_SERVER_ADDRESS = "localhost"
DEFAULT_SERVER_PORT = 9555
ALL_DIRECTIONS = list(Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST)


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
        self.socket_manager = SocketManager.SocketManager(server_address, server_port, verbose)

    def login(self):
        """Logs in to server"""
        self.socket_manager.connect()
        self.configure(ServerMessage.GameConfigMessage(self.socket_manager.receive_message(), \
        self.socket_manager))

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
                self.handle_begin_turn_message(ServerMessage.BeginTurnMessage(message))
            elif message.startswith("S|"): #Sonar Detection
                self.handle_sonar_detection_message(ServerMessage.SonarActivationMessage)
            elif message.startswith("D|"): #Detonation
                pass
            elif message.startswith("T|"): #Torpedo Hit
                pass
            elif message.startswith("O|"): #Discovered object
                pass
            elif message.startswith("I|"): #Sub info
                pass
            elif message.startswith("H|"): #player score
                pass
            elif message.startswith("F|"): #game finished
                pass
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
        self.issue_command()
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

    def issue_command(self):
        """Fancy AI logic for the sub"""
        #TODO
        pass

# if __name__ == '__main__':
#     if '--help' in sys.argv or '-h' in sys.argv:
#         print("Usage will go here") #TODO
#     username_arg = sys.argv[0] if sys.argv[0] is not None else DEFAULT_USERNAME
#     server_address_arg = sys.argv[1] if sys.argv[1] is not None else DEFAULT_SERVER_ADDRESS
#     server_port_arg = sys.argv[2] if sys.argv[2] is not None else DEFAULT_SERVER_PORT

#     bot = PySub(username_arg, server_address_arg, server_port_arg)
