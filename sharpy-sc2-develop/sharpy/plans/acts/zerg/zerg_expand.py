from sharpy.plans.acts import ActExpand
from sharpy.general.zone import Zone
from sc2.ids.unit_typeid import UnitTypeId


class ZergExpand(ActExpand):
    """Hard code 200 minerals into expansion."""

    def __init__(self, to_count: int, priority: bool = False):
        self.z_worker = None
        super().__init__(to_count, priority)

    def possibly_move_worker(self, zone: Zone):
        """Hard coded if 200 minerals, move worker."""
        available_minerals = self.ai.minerals - self.knowledge.reserved_minerals
        if not self.z_worker:
            self.z_worker = self.cache.own(UnitTypeId.DRONE).first
        position = zone.center_location

        if available_minerals >= 200:
            position = zone.center_location
            self.set_worker(self.z_worker)

            self.do(self.z_worker.move(position))
