from typing import List, Optional

from sc2.position import Point2
from sc2 import UnitTypeId, AbilityId
from sharpy.plans.tactics.scouting import ScoutBaseAction, Scout
from sharpy.plans.acts.zerg import ZergUnit


class OverlordScout(Scout):
    def __init__(self, *args: ScoutBaseAction):
        self.zerg_build = ZergUnit(UnitTypeId.OVERLORD)
        super().__init__(UnitTypeId.OVERLORD, 1, *args)

    async def start(self, knowledge: "Knowledge"):
        await self.zerg_build.start(knowledge)
        await super().start(knowledge)

    async def execute(self) -> bool:
        self.zerg_build.to_count = self.cache.own(UnitTypeId.OVERLORD).amount + 1
        await self.zerg_build.execute()
        return await super().execute()
