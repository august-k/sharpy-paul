"""Manage building post opener."""
from sc2 import Race
from sc2.ids.unit_typeid import UnitTypeId
from typing import Dict, Callable
from paul_plans.roach_ravager_swarmhost import RRSH
from paul_plans.opening import ViBE, LingRush
from sharpy.managers import ManagerBase
from sharpy.plans import BuildOrder

BUILDS: Dict[str, Callable[[], BuildOrder]] = {
    "ViBE": lambda: ViBE(),
    "ling_flood": lambda: LingRush(),
    "roach_ravager_swarmhost": lambda: RRSH(),
    # TODO: add enemy_one_base defense plan
}


class BuildSelector(ManagerBase):
    """Select builds based on information."""

    def __init__(self, build_name: str = "", follow_up: str = ""):
        """
        Set up initial build.
        @param build_name: name of opener
        @param follow_up: name of next build to transition to
        """
        if build_name:
            self.response = build_name
        else:
            self.response = "macro"
        if follow_up:
            self.next_build = follow_up
        else:
            self.next_build = "roach_ravager_swarmhost"

        super().__init__()

    async def update(self):
        """Update the build order."""
        if self.response == "ViBE":
            if self.knowledge.ai.vespene >= 92:
                self.response = "roach_ravager_swarmhost"
        elif self.response == "macro":
            if self.cache.own(UnitTypeId.HATCHERY).amount >= 3:
                self.response = "roach_ravager_swarmhost"

    async def post_update(self):
        """Override this if needed."""
        pass
