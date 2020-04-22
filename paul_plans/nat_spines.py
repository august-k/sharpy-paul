"""Build 4 spines at Natural against rushes."""
import math

import sc2
from sc2 import UnitTypeId, AbilityId
from sc2.position import Point2
from sc2.unit import Unit

from sharpy.plans.acts import ActBuilding


class NatSpines(ActBuilding):
    """
    Build 4 spines at Natural against rushes.

    Inherits ActBuilding. Overrides random location.
    """

    def __init__(self, to_count: int = 4):
        """We're only building spines with this Act and we default to 4."""
        count = to_count
        super().__init__(UnitTypeId.SPINECRAWLER, count)

    async def execute(self):
        """Includes pending in count."""
        count = self.get_count(self.unit_type, include_pending=True, include_not_ready=True)

        if count >= self.to_count:
            return True  # Step is done

        unit = self.ai._game_data.units[self.unit_type.value]
        cost = self.ai._game_data.calculate_ability_cost(unit.creation_ability)

        if self.knowledge.can_afford(self.unit_type):
            await self.actually_build(self.ai, count)
        else:
            self.knowledge.reserve(cost.minerals, cost.vespene)

        return False

    async def actually_build(self, ai, count):
        """Change building process to morph a spine."""
        location = self.get_random_build_location()
        self.knowledge.print(
            f"[ActBuilding] {count+1}. {self.unit_type.name} near ({location.x:.1f}, {location.y:.1f})"
        )
        worker = self.cache.own(UnitTypeId.DRONE).closest_to(location)
        self.do(worker(AbilityId.ZERGBUILD_SPINECRAWLER, location))

    def get_random_build_location(self) -> Point2:
        """
        4 spines by the natural.

        Changes the start point and distance.
        """
        start_point = self.knowledge.expansion_zones[1].center_location
        center = self.ai.game_info.map_center
        location = start_point.towards_with_random_angle(center, 4, math.pi / 2)
        return location
