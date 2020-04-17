from typing import List, Optional

from sc2.position import Point2
from sc2.units import Units
from sharpy.managers.roles import UnitTask
from sharpy.plans.acts import ActBase
from sc2.ids.unit_typeid import UnitTypeId
from sc2.unit import Unit


class OverlordScoutMain(ActBase):
    def __init__(self):
        self.scout_tag: int = 0
        super().__init__()

    async def start(self, knowledge: "Knowledge"):
        return await super().start(knowledge)

    async def execute(self) -> bool:
        overlords = self.cache.own(UnitTypeId.OVERLORD)
        scouts = self.roles.all_from_task(UnitTask.OverlordScout)
        scout_overlord = overlords.tags_in(scouts.tags)
        non_scout_overlords = overlords.tags_not_in(scouts.tags)

        if self.scout_tag:
            return True

        if not self.scout_tag and non_scout_overlords.amount > 1:
            scout_overlord = non_scout_overlords[0]
            self.scout_tag = scout_overlord.tag

        if scout_overlord:
            self.knowledge.roles.set_task(UnitTask.OverlordScout, scout_overlord)
            target = self.knowledge.expansion_zones[-1].behind_mineral_position_center

            self.do(scout_overlord.move(target))

        return True
