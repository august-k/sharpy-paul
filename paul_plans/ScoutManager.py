"""Receive scouting data and identify builds."""
from sharpy.managers.manager_base import ManagerBase
import enum


class EnemyRush(enum.IntEnum):
    Macro = 0
    # Zerg
    Pool12 = 1
    RoachRush = 2
    # Protoss
    CannonRush = 3
    # Terran
    EarlyMarines = 4


class ScoutManager(ManagerBase):
    """Manage scouting."""
    def __init__(self):
        super().__init__()
