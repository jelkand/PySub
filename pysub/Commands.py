"""Defines commands a submarine can send to the server"""
from util import *

class SubmarineCommand():
    """Base class for player commands"""
    def __init__(self, turn_number, sub_id):
        self.turn_number = turn_number
        self.sub_id = sub_id

class PingCommand(SubmarineCommand):
    """Command to use sonar"""
    def __init__(self, turn_number, sub_id):
        super().__init__(self, turn_number, sub_id)

    def __str__(self):
        return "P|{0}|{1}".format(self.turn_number, self.sub_id)

class SleepCommand(SubmarineCommand):
    """Command to sleep this turn and charge two modules"""
    def __init__(self, turn_number, sub_id, equip1, equip2):
        super().__init__(self, turn_number, sub_id)
        self.equip1 = equip1
        self.equip2 = equip2

    def __str__(self):
        return "S|{0}|{1}|{2}|{3}".format(self.turn_number, self.sub_id, self.equip1, self.equip2)

class MoveCommand(SubmarineCommand):
    """Command to move this turn and charge one module"""
    def __init__(self, turn_number, sub_id, direction, equip):
        super().__init__(self, turn_number, sub_id)
        self.direction = direction
        self.equip = equip

    def __str__(self):
        return "M|{0}|{1}|{2}|{3}".format(self.turn_number, self.sub_id, self.direction, self.equip)

class FireCommand(SubmarineCommand):
    """Command to fire a torpedo"""
    def __init__(self, turn_number, sub_id, destination):
        super().__init__(self, turn_number, sub_id)
        self.destination = destination

    def __str__(self):
        return "F|{0}|{1}|{2}".format(self.turn_number, self.sub_id, self.destination)

class SurfaceCommand(SubmarineCommand):
    """Command to surface and repair"""
    def __init__(self, turn_number, sub_id):
        super().__init__(self, turn_number, sub_id)

    def __str__(self):
        return "U|{0}|{1}".format(self.turn_number, self.sub_id)
