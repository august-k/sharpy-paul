from typing import List, TYPE_CHECKING

from sc2.ids.unit_typeid import UnitTypeId
from sc2.units import Units
from sc2.position import Point2
from sharpy.managers.roles import UnitTask
from sharpy.plans.acts import ActBase

if TYPE_CHECKING:
    from sharpy.knowledges import Knowledge


class RunBy(ActBase):
    units: Units

    def __init__(self, unit_type: UnitTypeId, unit_count: int, enemy_expansion: int):
        """
        Select a number of units to perform a run-by at an enemy base.
        @param unit_type: Type of unit to be used
        @param unit_count: Number of units to be used. Will not execute until enough units are available.
        @param enemy_expansion: Run-by target
        """
        self.unit_type = unit_type
        self.unit_count = unit_count
        self.ended = False
        self.target = enemy_expansion
        self.run_by_tags: List[int] = []
        super().__init__()

    async def start(self, knowledge: "Knowledge"):
        await super().start(knowledge)
        self.units = Units([], self.ai)

    async def execute(self) -> bool:
        if self.ended:
            return True
        destination = self.get_enemy_base_location(self.target)
        free_units = self.roles.get_types_from({self.unit_type}, UnitTask.Idle, UnitTask.Moving, UnitTask.Gathering)
        if len(free_units) >= self.unit_count:
            run_by_units = free_units.random_group_of(self.unit_count)
            for unit in run_by_units:
                self.roles.set_task(UnitTask.Reserved, unit)
                self.do(unit.move(destination))
            self.ended = True
        return True

    def get_enemy_base_location(self, expo: int) -> Point2:
        """
        Get Point2 of enemy base mineral line.
        @param expo: enemy expansion (0 for main, 1 for natural, 2 for third, etc.)
        @returns: Point2
        """
        return self.knowledge.zone_manager.enemy_expansion_zones[expo].behind_mineral_position_center
