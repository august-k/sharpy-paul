"""Plan for burrowing/unburrowing drones. Version 2."""

from sharpy.managers.roles import UnitTask
from sharpy.plans.acts import ActBase
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId


class PlanBurrowDrone(ActBase):
    """Plan for burrowing/unburrowing drones. Version 2."""

    def __init__(self):
        self.burrow_researched = False
        super().__init__()

    async def execute(self) -> True:
        """
        Iterate through Zones, burrowing and unburrowing based on safety.

        Drone: UnitTypeId.DRONE
        Burrowed Drone: UnitTypeId.DRONEBURROWED

        Args:
            None
        Returns:
            True: always proceed
        """
        if not self.burrow_researched:
            self.burrow_researched = UpgradeId.BURROW in self.ai.state.upgrades
        if not self.burrow_researched:
            # proceed with build order, but don't try to burrow/unburrow anything
            return True
        for zone in self.knowledge.zone_manager.expansion_zones:
            if zone.is_ours:
                if zone.is_under_attack:
                    # burrow if zone is in danger
                    for unit in zone.our_units(UnitTypeId.DRONE):
                        self.ai.do(unit(AbilityId.BURROWDOWN_DRONE))
                        self.knowledge.roles.set_task(UnitTask.BurrowedDrone, unit)
                else:
                    # unburrow once zone is safe
                    for unit in zone.our_units(UnitTypeId.DRONEBURROWED):
                        self.ai.do(unit(AbilityId.BURROWUP_DRONE))
                        self.knowledge.roles.clear_task(unit)
        return True
