"""Defines a generic submarine"""
from Commands import PingCommand, MoveCommand, FireCommand
from Util import Coordinate

class Submarine():
    """Generic submarine"""
    location = Coordinate(0, 0)
    dead = False
    active = True
    max_sonar_charge = False
    max_torpedo_charge = False
    size = 100
    shield_count = 3
    sonar_range = 0
    torpedo_range = 0

    def __init__(self, sub_id):
        self.sub_id = sub_id

    def update(self, info_message):
        """updates this sub's attributes based on a SubmarineInfoMessage"""
        if self.sub_id != info_message.sub_id:
            raise ValueError("sub_id {0} in info message doesn't match this sub's id: {1}" \
            .format(info_message.sub_id, self.sub_id))
        self.location = info_message.location
        self.dead = info_message.dead
        self.active = info_message.active
        self.max_sonar_charge = info_message.max_sonar_charge
        self.max_torpedo_charge = info_message.max_torpedo_charge
        self.shield_count = info_message.shield_count
        self.sonar_range = info_message.sonar_range
        self.torpedo_range = info_message.torpedo_range

    def get_x(self):
        """Returns the x coord of this sub"""
        return self.location.x

    def get_y(self):
        """returns the y coord of this sub"""
        return self.location.y

    def ping(self, turn_number):
        """Returns a PingCommand"""
        return PingCommand(turn_number, self.sub_id)

    def move(self, turn_number, direction, equip):
        """Returns a MoveCommand"""
        return MoveCommand(turn_number, self.sub_id, direction, equip)

    def fire_torpedo(self, turn_number, destination):
        """Returns a FireCommand"""
        return FireCommand(turn_number, self.sub_id, destination)
