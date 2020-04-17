from typing import List, Optional

from sc2.position import Point2
from sc2.units import Units
from sharpy.managers.roles import UnitTask
from sharpy.plans.acts import ActBase
from sc2.ids.unit_typeid import UnitTypeId
from sc2.unit import Unit


class OverlordScoutMain(ActBase):
    def __init__(self):
        self.scout_tags: List[int] = []
        super().__init__()

    async def start(self, knowledge: "Knowledge"):
        return await super().start(knowledge)

    async def execute(self) -> bool:
        overlords = self.cache.own(UnitTypeId.OVERLORD)
        scouts = self.roles.all_from_task(UnitTask.Scouting)
        scout_overlords = overlords.tags_in(scouts.tags)
        non_scout_overlords = overlords.tags_not_in(scouts.tags)

        if len(self.scout_tags) > 0 and not len(scout_overlords) == 0:
            return True

        if len(self.scout_tags) == 0 and non_scout_overlords.amount > 1:
            scout_overlords = Units(non_scout_overlords[0], self.ai)
            self.scout_tags = scout_overlords.tags

        for scout in scout_overlords:
            self.knowledge.roles.set_task(UnitTask.Scouting, scout)
            target = self.knowledge.expansion_zones[-1].behind_mineral_position_center

            self.do(scout.movee(target))

        return True
