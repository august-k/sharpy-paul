from typing import TYPE_CHECKING

from paul_plans.defensive_building import DefensiveBuilding, DefensePosition
from sc2.ids.unit_typeid import UnitTypeId
from sharpy.plans import BuildOrder, Step, StepBuildGas
from sharpy.plans.acts import ActBuilding
from sharpy.plans.acts.zerg import ZergUnit, AutoOverLord
from sharpy.plans.require import UnitExists, RequiredAll
from sharpy.plans.tactics import PlanDistributeWorkers

if TYPE_CHECKING:
    from sharpy.knowledges import Knowledge


class RoachRushResponse(BuildOrder):
    """Respond to a Roach Rush."""

    def __init__(self):
        """Create plan for build order."""
        self.drones = ZergUnit(UnitTypeId.DRONE, to_count=0)
        self.lings = ZergUnit(UnitTypeId.ZERGLING, to_count=999)
        self.queens = ZergUnit(UnitTypeId.QUEEN, to_count=3)
        self.roaches = ZergUnit(UnitTypeId.ROACH, to_count=100, priority=True)
        self.ravagers = ZergUnit(UnitTypeId.RAVAGER, to_count=0)
        self.defense_spines = DefensiveBuilding(
            unit_type=UnitTypeId.SPINECRAWLER, position_type=DefensePosition.Entrance, to_base_index=1, to_count=3
        )
        self.gas = StepBuildGas(to_count=3)

        unit_building = BuildOrder(
            [
                Step(None, self.drones, skip_until=self.should_build_drones),
                Step(UnitExists(UnitTypeId.SPAWNINGPOOL), self.defense_spines),
                Step(
                    RequiredAll([UnitExists(UnitTypeId.ROACHWARREN), UnitExists(UnitTypeId.ROACH)]),
                    self.ravagers,
                    skip_until=self.should_build_ravagers,
                ),
                Step(UnitExists(UnitTypeId.ROACHWARREN), self.roaches),
                Step(
                    RequiredAll(
                        [
                            UnitExists(UnitTypeId.SPAWNINGPOOL),
                            UnitExists(
                                UnitTypeId.ROACHWARREN,
                                include_pending=True,
                                include_not_ready=True,
                                include_killed=True,
                            ),
                        ]
                    ),
                    self.lings,
                ),
                Step(UnitExists(UnitTypeId.SPAWNINGPOOL), self.queens),
                Step(UnitExists(UnitTypeId.SPAWNINGPOOL), self.lings),
            ]
        )

        buildings: BuildOrder = BuildOrder(
            [
                Step(None, ActBuilding(UnitTypeId.SPAWNINGPOOL, to_count=1)),
                Step(UnitExists(UnitTypeId.SPAWNINGPOOL), ActBuilding(UnitTypeId.ROACHWARREN, to_count=1)),
                Step(None, self.gas, skip_until=self.should_build_gas),
            ]
        )

        super().__init__(buildings, unit_building)

    def should_build_drones(self, knowledge):
        """Determine if we need to build drones."""
        if self.cache.own(UnitTypeId.DRONE).amount >= 16 + self.get_count(UnitTypeId.EXTRACTOR) * 3:
            return False
        if not self.knowledge.game_analyzer.our_power.is_enough_for(
            self.knowledge.enemy_units_manager.enemy_total_power
        ):
            return False
        self.drones.to_count = 16 + self.get_count(UnitTypeId.EXTRACTOR) * 3
        return True

    def should_build_gas(self, knowledge):
        if (
            self.knowledge.game_analyzer.our_power.is_enough_for(self.knowledge.enemy_units_manager.enemy_total_power)
            and self.cache.own(UnitTypeId.DRONE).amount >= 16 * self.get_count(UnitTypeId.EXTRACTOR) * 3
        ):
            self.gas.to_count = min(3, self.get_count(UnitTypeId.EXTRACTOR) + 1)
            return True
        return False

    def should_build_ravagers(self, knowledge):
        if self.cache.own(UnitTypeId.ROACH).amount >= 10:
            self.ravagers.to_count = self.cache.own(UnitTypeId.ROACH).amount // 2
            return True
        return False
