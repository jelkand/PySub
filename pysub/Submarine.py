"""Defines a generic submarine"""
from Commands import *
from Util import *

class Submarine():
    """Generic submarine"""
    location = Coordinate(0, 0)
    dead = False
    active = True
    max_sonar_charge = False
    max_torpedo_charge = False
    size = 100
    shield_count = 3
    torpedo_count = -1 # -1 = unlimited
    sonar_range = 0
    torpedo_range = 0
    reactor_damage = 0
    surface_turns_remaining = 0

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
        self.torpedo_count = info_message.torpedo_count
        self.sonar_range = info_message.sonar_range
        self.torpedo_range = info_message.torpedo_range
        self.reactor_damage = info_message.reactor_damage
        self.surface_turns_remaining = info_message.surface_turns_remaining

    def get_x(self):
        """Returns the x coord of this sub"""
        return self.location.x

    def get_y(self):
        """returns the y coord of this sub"""
        return self.location.y

    def has_unlimited_torpedos(self):
        """Returns true if this sub has unlimited torpedos"""
        return self.torpedo_count < 0

    def is_surfaced(self):
        """Returns true if this sub has turns remaining on the surface"""
        return self.surface_turns_remaining > 0

    def ping(self, turn_number):
        """Returns a PingCommand"""
        return PingCommand(turn_number, self.sub_id)

    def sleep(self, turn_number, equip1, equip2):
        """Returns a SleepCommand"""
        return SleepCommand(turn_number, self.sub_id, equip1, equip2)

    def move(self, turn_number, direction, equip):
        """Returns a MoveCommand"""
        return MoveCommand(turn_number, self.sub_id, direction, equip)

    def fire_torpedo(self, turn_number, destination):
        """Returns a FireCommand"""
        return FireCommand(turn_number, self.sub_id, destination)

    def surface(self, turn_number):
        """Returns a SurfaceCommand"""
        return SurfaceCommand(turn_number, self.sub_id)
