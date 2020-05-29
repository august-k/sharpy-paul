from sharpy.managers.combat2 import MicroStep
from sc2.unit import Unit
from sc2.units import Units
from sharpy.managers.combat2 import Action


class SuicideLingMicro(MicroStep):
    def group_solve_combat(self, units: Units, current_command: Action) -> Action:
        if self.closest_group:
            return Action(self.closest_group.center, True)
        else:
            return Action(self.knowledge.enemy_expansion_zones[0].center_location, True)

    def unit_solve_combat(self, unit: Unit, current_command: Action) -> Action:
        if self.closest_group:
            return Action(self.closest_group.center, True)
        else:
            return Action(self.knowledge.enemy_expansion_zones[0].center_location, True)
