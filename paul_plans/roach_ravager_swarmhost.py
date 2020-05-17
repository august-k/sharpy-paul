"""Roach Ravager Swarmhost composition."""
from typing import Set, Union

from sc2.ids.unit_typeid import UnitTypeId

from paul_plans.basic_upgrades import StandardUpgrades
from paul_plans.mass_expand import MassExpand
from paul_plans.nat_spines import NatSpines
from sharpy.plans import BuildOrder, SequentialList, Step, StepBuildGas
from sharpy.plans.acts import ActBuilding, ActExpand, ActTech
from sharpy.plans.acts.zerg import AutoOverLord, MorphLair, MorphRavager, ZergUnit
from sharpy.plans.require import RequireCustom, RequiredAll, RequiredTechReady, UnitExists, RequiredTime
from sharpy.plans.tactics.scouting import ScoutLocation
from sharpy.plans.tactics.zerg import LingScout
from paul_plans.run_by import RunBy


class RRSH(BuildOrder):
    """Roach ravager swarmhost build."""

    def __init__(self):
        """Create the build order."""
        self.drone = ZergUnit(UnitTypeId.DRONE, to_count=0)
        self.queen = ZergUnit(UnitTypeId.QUEEN, to_count=3, priority=True)
        self.zergling = ZergUnit(UnitTypeId.ZERGLING, to_count=0)
        self.roach = ZergUnit(UnitTypeId.ROACH, to_count=0)
        self.ravager = MorphRavager(target_count=0)
        self.swarmhost = ZergUnit(UnitTypeId.SWARMHOSTMP, to_count=0)
        ling_scout = BuildOrder([Step(RequiredTime(4 * 60), LingScout(2, ScoutLocation.scout_enemy3()))])
        run_by = Step(
            RequiredTime(4 * 60), RunBy(UnitTypeId.ZERGLING, 8, 1)
        )
        units = BuildOrder(
            [
                Step(None, self.drone),
                Step(UnitExists(UnitTypeId.SPAWNINGPOOL), self.queen),
                Step(UnitExists(UnitTypeId.INFESTATIONPIT), self.swarmhost),
                Step(UnitExists(UnitTypeId.ROACHWARREN), self.roach),
                Step(UnitExists(UnitTypeId.ROACH), self.ravager),
                Step(UnitExists(UnitTypeId.SPAWNINGPOOL), self.zergling),
            ]
        )
        self.gas = StepBuildGas(to_count=0)
        tech_buildings = BuildOrder(
            Step(
                UnitExists(UnitTypeId.DRONE, 30),
                BuildOrder(
                    [
                        Step(None, ActBuilding(UnitTypeId.ROACHWARREN)),
                        Step(None, MorphLair()),
                        Step(
                            RequiredAll(
                                [
                                    UnitExists(UnitTypeId.LAIR),
                                    UnitExists(UnitTypeId.EVOLUTIONCHAMBER),
                                    UnitExists(UnitTypeId.HATCHERY, 3),
                                ]
                            ),
                            ActBuilding(UnitTypeId.INFESTATIONPIT),
                        ),
                        Step(None, ActBuilding(UnitTypeId.EVOLUTIONCHAMBER)),
                        Step(UnitExists(UnitTypeId.HATCHERY, 4), ActBuilding(UnitTypeId.EVOLUTIONCHAMBER, 2)),
                    ]
                ),
            )
        )
        bases = BuildOrder(
            [
                Step(None, ActExpand(to_count=3, priority=True, consider_worker_production=False)),
                Step(UnitExists(UnitTypeId.DRONE, 60), ActExpand(4, priority=True, consider_worker_production=False)),
            ]
        )

        nat_spines = Step(
            UnitExists(UnitTypeId.SPAWNINGPOOL),
            NatSpines(4),
            skip=UnitExists(UnitTypeId.SPINECRAWLER, count=4),
            skip_until=lambda k: k.build_detector.rush_detected,
        )
        super().__init__(
            [
                nat_spines,
                units,
                tech_buildings,
                self.gas,
                bases,
                MassExpand(),
                AutoOverLord(),
                StandardUpgrades(),
                # ling_scout,
                run_by,
            ]
        )

    def safe(self, knowledge="Knowledge"):
        """See if any zones are under attack."""
        for zone in self.knowledge.zone_manager.expansion_zones:
            if zone.is_ours and zone.is_under_attack:
                return False
        if self.knowledge.game_analyzer.army_at_least_small_disadvantage and self.close_unit():
            return False
        return True

    def close_unit(self, knowledge="Knowledge"):
        """Check how close the nearest enemy unit is."""
        nat = self.knowledge.zone_manager.expansion_zones[1].center_location
        for unit in self.knowledge.ai.enemy_units:
            if self.knowledge.ai._distance_pos_to_pos(unit.position, nat) < 50:
                return True
        return False

    async def execute(self):
        """Assign amounts of units to build."""
        self.gas.to_count = min((self.get_count(UnitTypeId.HATCHERY) - 1) * 2, 8)
        # set_this_iteration = set()
        # larva = self.knowledge.unit_cache.own(UnitTypeId.LARVA).amount
        # if not larva:
        #     # we have no larva, don't build anything
        #     self.queen.to_count = self.get_count(UnitTypeId.HATCHERY) + 3
        #     self.ravager.target_count = self.cache.own(UnitTypeId.ROACH).amount
        #     set_this_iteration.add(self.ravager)
        #     self.set_to_zero(set_this_iteration)
        #     return await super().execute()
        if self.get_count(UnitTypeId.SPINECRAWLER, include_not_ready=True, include_pending=True) >= 2 or self.safe():
            target_drone_number = min(
                self.get_count(UnitTypeId.HATCHERY) * 16 + self.get_count(UnitTypeId.EXTRACTOR) * 3, 85
            )
            if self.cache.own(UnitTypeId.DRONE).amount != target_drone_number:
                self.drone.to_count = target_drone_number
                # set_this_iteration.add(self.drone)
                # if target_drone_number - self.cache.own(UnitTypeId.DRONE).amount > larva:
                #     # all larva going to drones
                #     return await super().execute()
        # either we're under attack or we've reached our drone threshold
        if self.get_count(UnitTypeId.INFESTATIONPIT):
            self.swarmhost.to_count = 15
            # set_this_iteration.add(self.swarmhost)
        if self.cache.own(UnitTypeId.ROACH).amount:
            self.ravager.target_count = self.cache.own(UnitTypeId.ROACH).amount
            # set_this_iteration.add(self.ravager)
        if self.get_count(UnitTypeId.ROACHWARREN):
            self.roach.to_count = self.ai.vespene - self.knowledge.reserved_gas / 25
            # set_this_iteration.add(self.roach)
        if self.get_count(UnitTypeId.SPAWNINGPOOL):
            self.zergling.to_count = 100
            # set_this_iteration.add(self.zergling)
        # self.set_to_zero(set_this_iteration)
        return await super().execute()

    # def set_to_zero(self, exclude: Set[Union[ZergUnit, MorphRavager]] = set()):
    #     """Set all to_counts to 0 unless we want to build some this iteration."""
    #     for u in {self.drone, self.zergling, self.roach, self.ravager, self.swarmhost}:
    #         if u not in exclude:
    #             u.to_count = 0
