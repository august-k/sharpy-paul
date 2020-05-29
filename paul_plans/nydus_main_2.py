from sharpy.plans.acts import ActBase, ActBuilding
from sharpy.managers.combat2 import MicroRules, NoMicro
from sc2.units import Units
from sc2.ids.unit_typeid import UnitTypeId
from sc2.position import Point2
from sharpy.plans.acts.zerg import MorphLair, ZergUnit
import numpy as np


class NydusLingMain(ActBase):
    """Set up Nydus in their main."""
    units: Units

    def __init__(self, amount: int):
        super().__init__()
        # custom micro to make sure lings just attack
        self.micro = MicroRules()
        self.micro.load_default_methods()
        self.micro.generic_micro = NoMicro()

        self.started = False
        self.ended = False

        self.amount = amount
        self.lair_tech = MorphLair()
        self.network = ActBuilding(UnitTypeId.NYDUSNETWORK, to_count=1)
        self.zerg_build = ZergUnit(UnitTypeId.ZERGLING)
        self.nydus_spot: Point2 = Point2((0, 0))

    async def start(self, knowledge: "Knowledge"):
        await super().start(knowledge)
        await self.lair_tech.start(knowledge)
        await self.network.start(knowledge)
        await self.zerg_build.start(knowledge)
        await self.micro.start(knowledge)
        self.units = Units([], self.ai)
        self.nydus_spot = self.calculate_nydus_location()

    async def execute(self) -> bool:
        if self.ended:
            return True

        # get a lair
        if not self.get_count(UnitTypeId.LAIR, include_pending=True, include_not_ready=True) + self.get_count(UnitTypeId.HIVE):
            await self.lair_tech.execute()
            return True

        # make sure we'll have enough units
        if self.cache.own(UnitTypeId.ZERGLING) < self.amount:
            self.zerg_build.to_count = self.amount
            await self.zerg_build.execute()
            return True

        # pause until we have a lair
        if not self.get_count(UnitTypeId.LAIR, include_not_ready=False, include_pending=False) + self.get_count(UnitTypeId.HIVE, include_not_ready=True, include_pending=True):
            return True

        # build a Nydus Network
        if not self.get_count(UnitTypeId.NYDUSNETWORK, include_pending=True, include_not_ready=True):
            await self.network.execute()
            return True

        # pause until we have a Nydus Network
        if not self.get_count(UnitTypeId.NYDUSNETWORK):
            return True

    def calculate_nydus_location(self):
        # first get all highground tiles
        max_height: int = np.max(self.ai.game_info.terrain_height.data_numpy)
        highground_spaces: np.array = np.where(self.ai.game_info.terrain_height.data_numpy == max_height)

        # stack the y and x coordinates together, transpose the matrix for
        # easier use, this then reflects x and y coordinates
        all_highground_tiles: np.array = np.vstack((highground_spaces[1], highground_spaces[0])).transpose()

        # get distances of high ground tiles to start
        dist_from_start: np.array = self.calculate_distance_points_from_location(
            self.knowledge.enemy_start_location, all_highground_tiles
        )
        # get ids of all tiles that are closer than 30
        valid_tiles_start: np.array = np.where(dist_from_start < 30)[0]
        return valid_tiles_start

    def calculate_distance_points_from_location(self, start: Point2, points: np.array) -> np.array:
        """Determine distance from point to start location."""
        sl = np.array([start[0], start[1]])
        sl = np.expand_dims(sl, 0)
        # euclidean distance on multiple points to a single point
        dist = (points - sl) ** 2
        dist = np.sum(dist, axis=1)
        dist = np.sqrt(dist)
        return dist