"""Receive scouting data and identify builds."""
from typing import Set
from abc import ABC
from sc2.position import Point2
from sc2.player import Race
from sc2.ids.unit_typeid import UnitTypeId
from sharpy.managers.manager_base import ManagerBase
import enum


class EnemyBuild(enum.IntEnum):
    """Enum of possible detected builds."""
    Macro = 0
    GeneralRush = 1
    # Zerg
    Pool12 = 2
    RoachRush = 3
    LingRush = 4
    # Protoss
    CannonRush = 5
    # Terran
    EarlyMarines = 6
    BCRush = 7
    TankMech = 8
    Bio = 9


class TerranFlags(enum.IntEnum):
    """Flags for things all builds should account for."""
    StarportTechLab = 0
    ProxyBarracks = 1
    MissingInfoSpore = 2
    BattleCruisers = 3
    Gasless = 4
    OneBaseHeavyGas = 5


class ScoutManager(ManagerBase, ABC):
    """Manage scouting information."""

    def __init__(self):
        """Set up variables."""
        super().__init__()
        self.main_seen = False
        self.flags: Set[int] = set()
        self.enemy_build = EnemyBuild.Macro
        self.enemy_natural: Point2 = Point2((0, 0))
        self.half_rush_point: int = 0

    async def start(self, knowledge):
        """Set up game data."""
        self.knowledge = knowledge
        self._debug = self.knowledge.config["debug"].getboolean(type(self).__name__)
        self.ai = knowledge.ai
        # This is Infy's fault
        # noinspection PyProtectedMember
        self.client = self.ai._client
        self.cache = knowledge.unit_cache
        self.unit_values = knowledge.unit_values
        self.enemy_natural = self.knowledge.enemy_expansion_zones[1].center_location
        self.half_rush_point = self.knowledge.rush_distance // 2

    async def update(self):
        """Update build detection based on scouting data."""
        if self.enemy_build == EnemyBuild.Macro and self.ai.is_visible(self.enemy_natural):
            if self.ai.in_pathing_grid(self.enemy_natural) and self.knowledge.enemy_townhalls.amount == 1:
                # enemy has not expanded to their natural and we only know of one townhall
                self.enemy_build = EnemyBuild.GeneralRush
        if self.ai.enemy_race == Race.Zerg:
            self.zerg_scout()
        elif self.ai.enemy_race == Race.Protoss:
            self.protoss_scout()
        elif self.ai.enemy_race == Race.Terran:
            self.terran_scout()

    async def post_update(self):
        pass

    def zerg_scout(self):
        """ZvZ scouting."""
        if (self.knowledge.known_enemy_structures(UnitTypeId.ROACHWARREN) and self.ai.time <= 4 * 60) or (
            self.knowledge.known_enemy_units(UnitTypeId.ROACH) and self.ai.time <= 4 * 60
        ):
            self.enemy_build = EnemyBuild.RoachRush

        if (self.knowledge.known_enemy_units(UnitTypeId.ZERGLING).amount > 6 and self.ai.time <= 3 * 60) or (
            self.knowledge.known_enemy_units(UnitTypeId.ZERGLING).amount >= 6
            and self.knowledge.known_enemy_workers.closer_than(20, self.knowledge.expansion_zones[1].center_location)
            or (
                self.knowledge.known_enemy_units(UnitTypeId.ZERGLING).closer_than(
                    self.half_rush_point, self.knowledge.expansion_zones[1].center_location
                )
            )
        ):
            self.enemy_build = EnemyBuild.LingRush

    def protoss_scout(self):
        """ZvP scouting. Not really implemented."""
        if self.knowledge.known_enemy_units(UnitTypeId.ZEALOT):
            # yeah, yeah, it's a Terran build. I just want to go Ling Bane. Fight me.
            self.enemy_build = EnemyBuild.Bio

    def terran_scout(self):
        """ZvT scouting."""

        if not self.main_seen:
            if self.knowledge.ai.is_visible(self.knowledge.enemy_start_location):
                self.main_seen = True

        if not self.main_seen and self.ai.time >= 4 * 60:
            self.flags.add(TerranFlags.MissingInfoSpore)

        if self.main_seen and self.ai.time >= 2 * 60:
            if not self.knowledge.known_enemy_structures(UnitTypeId.EXTRACTOR):
                self.flags.add(TerranFlags.Gasless)
            else:
                if TerranFlags.Gasless in self.flags:
                    self.flags.remove(TerranFlags.Gasless)

        if self.knowledge.known_enemy_structures(UnitTypeId.BARRACKS):
            if (
                self.knowledge.known_enemy_structures(UnitTypeId.BARRACKS).closest_distance_to(
                    self.knowledge.expansion_zones[1].center_location
                )
                < self.knowledge.rush_distance // 2
            ):
                self.flags.add(TerranFlags.ProxyBarracks)
            else:
                if TerranFlags.ProxyBarracks in self.flags:
                    self.flags.remove(TerranFlags.ProxyBarracks)

        if self.knowledge.known_enemy_structures(UnitTypeId.STARPORTTECHLAB):
            self.flags.add(TerranFlags.StarportTechLab)

        if self.knowledge.known_enemy_units(UnitTypeId.MARINE) or self.knowledge.known_enemy_units(UnitTypeId.REAPER):
            self.enemy_build = EnemyBuild.Bio

        if (
            self.knowledge.known_enemy_units(UnitTypeId.SIEGETANK).amount
            + self.knowledge.known_enemy_units(UnitTypeId.SIEGETANKSIEGED).amount
        ) and not self.knowledge.known_enemy_units(UnitTypeId.MARINE):
            self.enemy_build = EnemyBuild.TankMech

        if self.knowledge.known_enemy_structures(UnitTypeId.FUSIONCORE) and self.ai.time <= 7 * 60:
            self.enemy_build = EnemyBuild.BCRush
            self.flags.add(TerranFlags.BattleCruisers)

        if self.knowledge.known_enemy_units(UnitTypeId.BATTLECRUISER) and self.ai.time <= 7 * 60:
            self.enemy_build = EnemyBuild.BCRush
            self.flags.add(TerranFlags.BattleCruisers)
