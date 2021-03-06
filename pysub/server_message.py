"""Methods for managing server messages"""
from util import Coordinate

class ServerMessage:
    """Base class of server messages"""

    def __init__(self, prefix, message_type, min_part_count, message):
        self.parts = message.split("|") if message is not None else list()
        if not message.startswith(prefix) or len(self.parts) < min_part_count:
            raise ValueError("Invalid {0} message: {1}".format(message_type, message))
        self.part_count = len(self.parts)

    def get_part(self, idx):
        """returns part at index"""
        return self.parts[idx]

class GameSettingMessage(ServerMessage):
    """Messages for game settings"""
    prefix = "V"
    message_type = "game setting"
    min_part_count = 3
    values = list()

    def __init__(self, message):
        super(GameSettingMessage, self).__init__(self.prefix, self.message_type, self.min_part_count, message)
        self.setting_name = self.get_part(1)
        for idx in range(2, self.part_count):
            self.values.append(self.get_part(idx))

class GameConfigMessage(ServerMessage):
    """Messages for custom game settings"""
    prefix = "C"
    message_type = "game config"
    min_part_count = 5
    custom_settings = list()

    def __init__(self, message, socket_manager):
        super(GameConfigMessage, self).__init__(self.prefix, self.message_type, self.min_part_count, message)
        self.server_version = self.get_part(1)
        self.game_title = self.get_part(2)
        self.map_width = int(self.get_part(3))
        self.map_height = int(self.get_part(4))
        self.settings_count = int(self.get_part(5))

        for _ in range(self.settings_count):
            self.custom_settings.append(GameSettingMessage(socket_manager.receive_message()))

class TurnMessage(ServerMessage):
    """message for turn info"""
    def __init__(self, prefix, message_type, min_part_count, message):
        super(TurnMessage, self).__init__(prefix, message_type, min_part_count, message)
        self.turn_number = int(self.get_part(1))

class BeginTurnMessage(TurnMessage):
    """Begins turn"""
    prefix = "B"
    message_type = "begin turn"
    min_part_count = 2

    def __init__(self, message):
        super(BeginTurnMessage, self).__init__(self.prefix, self.message_type, self.min_part_count, message)

class SonarDetectionMessage(TurnMessage):
    """Message recording sonar activations in the turn"""
    prefix = "S"
    message_type = "sonar detection"
    min_part_count = 4

    def __init__(self, message):
        super(SonarDetectionMessage, self).__init__(self.prefix, self.message_type, self.min_part_count, message)

class DetonationMessage(TurnMessage):
    """Message of detonation that occurred in this turn"""
    prefix = "D"
    message_type = "detonation"
    min_part_count = 5

    def __init__(self, message):
        super(DetonationMessage, self).__init__(self.prefix, self.message_type, self.min_part_count, message)
        self.location = Coordinate(int(self.get_part(2)), int(self.get_part(3)))
        self.radius = int(self.get_part(4))

class DiscoveredObjectMessage(TurnMessage):
    """Message notifying of objects discovered by sonar"""
    prefix = "O"
    message_type = "discovered object"
    min_part_count = 5

    def __init__(self, message):
        super(DiscoveredObjectMessage, self).__init__(self.prefix, self.message_type, self.min_part_count, message)
        self.location = Coordinate(int(self.get_part(2)), int(self.get_part(3)))
        self.size = int(self.get_part(4))

class TorpedoHitMessage(TurnMessage):
    """Message notifying player of their hits."""
    prefix = "T"
    message_type = "torpedo hit"
    min_part_count = 5

    def __init__(self, message):
        super(TorpedoHitMessage, self).__init__(self.prefix, self.message_type, self.min_part_count, message)
        self.location = Coordinate(self.get_part(2), self.get_part(3))
        self.damage = int(self.get_part(4))

class SubmarineInfoMessage(TurnMessage):
    """Message sent to each player to relay status of submarine"""
    prefix = "I"
    message_type = "submarine info"
    min_part_count = 6

    dead = False
    shield_count = 0
    sonar_range = 0
    torpedo_range = 0
    max_sonar_charge = False
    max_torpedo_charge = False

    def __init__(self, message):
        super(SubmarineInfoMessage, self).__init__(self.prefix, self.message_type, self.min_part_count, message)
        self.sub_id = int(self.get_part(2))
        self.location = Coordinate(int(self.get_part(3)), int(self.get_part(4)))
        self.active = (self.get_part(5) == 1)

        for i in range(6, self.part_count):
            split = self.get_part(i).split('=')
            if len(split) != 2:
                raise ValueError("invalid submarine info message: {0}".format(message))
            elif split[0] == "shields":
                self.shield_count = int(split[1])
            elif split[0] == "size":
                self.size = int(split[1])
            elif split[0] == "torpedos":
                self.torpedo_count = int(split[1])
            elif split[0] == "sonar_range":
                self.sonar_range = int(split[1])
            elif split[0] == "max_sonar":
                self.max_sonar_charge = split[1]
            elif split[0] == "torpedo_range":
                self.torpedo_range = int(split[1])
            elif split[0] == "max_torpedo":
                self.max_torpedo_charge = split[1]
            elif split[0] == "reactor_damage":
                self.reactor_damage = split[1]
            elif split[0] == "dead":
                self.dead = split[1] == 1

class PlayerScoreMessage(TurnMessage):
    """Notifies player of their score"""
    prefix = "H"
    message_type = "player score"
    min_part_count = 3

    def __init__(self, message):
        super(PlayerScoreMessage, self).__init__(self.prefix, self.message_type, self.min_part_count, message)
        self.score = self.get_part(2)

class PlayerResultMessage(ServerMessage):
    """Player results"""
    prefix = "P"
    message_type = "player result"
    min_part_count = 3

    def __init__(self, message):
        super(PlayerResultMessage, self).__init__(self.prefix, self.message_type, self.min_part_count, message)
        self.player_name = self.get_part(1)
        self.player_score = int(self.get_part(2))

class GameFinishedMessage(ServerMessage):
    """Reports result of the game"""
    prefix = "F"
    message_type = "game finished"
    min_part_count = 4
    player_results = list()

    def __init__(self, message, socket_manager):
        super(GameFinishedMessage, self).__init__(self.prefix, self.message_type, self.min_part_count, message)
        self.player_count = int(self.get_part(1))
        self.turn_count = int(self.get_part(2))
        self.game_state = self.get_part(3)
        for _ in range(self.player_count):
            self.player_results.append(PlayerResultMessage(socket_manager.receive_message()))
            