"""Manage building post opener."""
from sc2 import Race
from sc2.ids.unit_typeid import UnitTypeId
from typing import Dict, Callable
from paul_plans.opening import ViBE, LingRush
from sharpy.managers import ManagerBase
from sharpy.plans import BuildOrder

BUILDS: Dict[str, Callable[[], BuildOrder]] = {
    "default": lambda: ViBE(),
    "ViBE": lambda: ViBE(),
    "ling_flood": lambda: LingRush(),
    # TODO: add enemy_one_base defense plan
}


class BuildSelector(ManagerBase):
    """Select builds based on information."""

    def __init__(self, build_name: str):
        """Set up builds."""
        self.dynamic = build_name == "default"
        if self.dynamic:
            assert build_name in BUILDS.keys()
            self.response = build_name
        else:
            self.response = "ViBE"
        self.townhall: UnitTypeId

        super().__init__()

    async def update(self):
        """Update the build order."""
        if not self.dynamic:
            return

        if self.knowledge.build_detector.rush_detected:
            self.response = "rush_defense"
        else:
            pass

    async def post_update(self):
        """Override this if needed."""
        pass
