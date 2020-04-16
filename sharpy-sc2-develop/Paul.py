"""Hard coded opening."""
import random
from typing import Set

import sc2
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.player import Bot, Computer, Difficulty, Race

from paul_plans import MassExpand, retrieve_build
from paul_plans.opening import LingRush
from sharpy.knowledges import KnowledgeBot
from sharpy.managers.game_states.advantage import at_least_small_disadvantage
from sharpy.plans import BuildOrder, SequentialList, Step, StepBuildGas
from sharpy.plans.acts import ActBuilding, ActTech
from sharpy.plans.acts.zerg import (
    AutoOverLord,
    MorphHive,
    MorphLair,
    MorphRavager,
    ZergUnit,
)
from sharpy.plans.require import (
    RequiredAll,
    RequiredSupply,
    RequiredTechReady,
    RequiredUnitExists,
    RequiredUnitReady,
)
from sharpy.plans.tactics import (
    HostPlanZoneAttack,
    PlanDistributeWorkers,
    PlanFinishEnemy,
    PlanWorkerOnlyDefense,
    PlanZoneDefense,
    PlanZoneGather,
    WorkerScout,
)
from sharpy.plans.tactics.zerg import (
    InjectLarva,
    OverlordScout,
    CounterTerranTie,
    PlanBurrowDrone,
)


class PaulBuild(BuildOrder):
    """
    Build order for Paul after the opening.
    """

    def __init__(self):
        """Build order steps to be combined."""
        super().__init__([LarvaBuild(), MassExpand(), AutoOverLord(), Tech()])


class Tech(BuildOrder):
    """
    Conditions for building tech structures and upgrades.
    """

    def __init__(self):
        self.flier_found = False
        tech_buildings = BuildOrder(
            [
                Step(
                    RequiredAll(
                        [
                            RequiredUnitExists(UnitTypeId.HATCHERY, 3, include_pending=False, include_not_ready=False,),
                            RequiredUnitExists(UnitTypeId.DRONE, 60),
                        ],
                    ),
                    MorphLair(),
                ),
                Step(RequiredUnitExists(UnitTypeId.LAIR, include_pending=True), ActBuilding(UnitTypeId.ROACHWARREN),),
                Step(
                    RequiredUnitExists(UnitTypeId.LAIR, include_pending=True), ActBuilding(UnitTypeId.EVOLUTIONCHAMBER),
                ),
                Step(RequiredUnitExists(UnitTypeId.LAIR), ActBuilding(UnitTypeId.INFESTATIONPIT),),
                Step(
                    RequiredUnitExists(UnitTypeId.LAIR),
                    ActBuilding(UnitTypeId.HYDRALISKDEN),
                    skip_until=self.enemy_fliers,
                ),
                Step(
                    RequiredAll(
                        [
                            RequiredUnitExists(UnitTypeId.LAIR),
                            RequiredUnitExists(UnitTypeId.INFESTATIONPIT),
                            RequiredTechReady(UpgradeId.ZERGGROUNDARMORSLEVEL2),
                        ]
                    ),
                    MorphHive(),
                ),
            ]
        )

        self.gas_buildings = StepBuildGas(to_count=0)

        unit_upgrades = BuildOrder(
            [
                Step(
                    RequiredUnitReady(UnitTypeId.ROACHWARREN),
                    ActTech(UpgradeId.GLIALRECONSTITUTION, UnitTypeId.ROACHWARREN),
                ),
                Step(
                    RequiredUnitReady(UnitTypeId.HYDRALISKDEN),
                    ActTech(UpgradeId.EVOLVEGROOVEDSPINES, UnitTypeId.HYDRALISKDEN),
                ),
                Step(
                    RequiredUnitReady(UnitTypeId.HYDRALISKDEN),
                    ActTech(UpgradeId.EVOLVEMUSCULARAUGMENTS, UnitTypeId.HYDRALISKDEN),
                ),
            ]
        )

        generic_upgrades = SequentialList(
            [
                Step(
                    RequiredUnitReady(UnitTypeId.EVOLUTIONCHAMBER),
                    ActTech(UpgradeId.ZERGMISSILEWEAPONSLEVEL1, UnitTypeId.EVOLUTIONCHAMBER),
                ),
                Step(
                    RequiredAll(
                        [
                            RequiredUnitReady(UnitTypeId.EVOLUTIONCHAMBER),
                            RequiredTechReady(UpgradeId.ZERGMISSILEWEAPONSLEVEL1),
                        ]
                    ),
                    ActTech(UpgradeId.ZERGMISSILEWEAPONSLEVEL2, UnitTypeId.EVOLUTIONCHAMBER),
                ),
                Step(
                    RequiredAll(
                        [
                            RequiredUnitReady(UnitTypeId.EVOLUTIONCHAMBER),
                            RequiredTechReady(UpgradeId.ZERGMISSILEWEAPONSLEVEL2),
                        ]
                    ),
                    ActTech(UpgradeId.ZERGGROUNDARMORSLEVEL1, UnitTypeId.EVOLUTIONCHAMBER),
                ),
                Step(
                    RequiredAll(
                        [
                            RequiredUnitReady(UnitTypeId.EVOLUTIONCHAMBER),
                            RequiredTechReady(UpgradeId.ZERGGROUNDARMORSLEVEL1),
                        ]
                    ),
                    ActTech(UpgradeId.ZERGGROUNDARMORSLEVEL2, UnitTypeId.EVOLUTIONCHAMBER),
                ),
                Step(
                    RequiredAll(
                        [
                            RequiredUnitReady(UnitTypeId.EVOLUTIONCHAMBER),
                            RequiredTechReady(UpgradeId.ZERGGROUNDARMORSLEVEL2),
                        ]
                    ),
                    ActTech(UpgradeId.ZERGMELEEWEAPONSLEVEL1, UnitTypeId.EVOLUTIONCHAMBER),
                ),
                Step(
                    RequiredAll(
                        [
                            RequiredUnitReady(UnitTypeId.EVOLUTIONCHAMBER),
                            RequiredTechReady(UpgradeId.ZERGMELEEWEAPONSLEVEL1),
                        ]
                    ),
                    ActTech(UpgradeId.ZERGMELEEWEAPONSLEVEL2, UnitTypeId.EVOLUTIONCHAMBER),
                ),
                Step(
                    RequiredAll(
                        [
                            RequiredUnitReady(UnitTypeId.EVOLUTIONCHAMBER),
                            RequiredUnitExists(UnitTypeId.HIVE),
                            RequiredTechReady(UpgradeId.ZERGMELEEWEAPONSLEVEL2),
                        ]
                    ),
                    ActTech(UpgradeId.ZERGMISSILEWEAPONSLEVEL3, UnitTypeId.EVOLUTIONCHAMBER),
                ),
                Step(
                    RequiredAll(
                        [
                            RequiredUnitReady(UnitTypeId.EVOLUTIONCHAMBER),
                            RequiredUnitExists(UnitTypeId.HIVE),
                            RequiredTechReady(UpgradeId.ZERGMISSILEWEAPONSLEVEL3),
                        ]
                    ),
                    ActTech(UpgradeId.ZERGGROUNDARMORSLEVEL3, UnitTypeId.EVOLUTIONCHAMBER),
                ),
                Step(
                    RequiredAll(
                        [
                            RequiredUnitReady(UnitTypeId.EVOLUTIONCHAMBER),
                            RequiredUnitExists(UnitTypeId.HIVE),
                            RequiredTechReady(UpgradeId.ZERGGROUNDARMORSLEVEL3),
                        ]
                    ),
                    ActTech(UpgradeId.ZERGMELEEWEAPONSLEVEL3, UnitTypeId.EVOLUTIONCHAMBER),
                ),
            ]
        )

        misc_upgrades = BuildOrder(
            [
                Step(
                    RequiredTechReady(UpgradeId.ZERGLINGMOVEMENTSPEED),
                    ActTech(UpgradeId.OVERLORDSPEED, UnitTypeId.HATCHERY),
                ),
                Step(RequiredUnitExists(UnitTypeId.LAIR), ActTech(UpgradeId.BURROW, UnitTypeId.HATCHERY),),
            ]
        )

        super().__init__([tech_buildings, self.gas_buildings, unit_upgrades, generic_upgrades, misc_upgrades])

    async def execute(self):
        hatches = self.get_count(UnitTypeId.HATCHERY)
        if hatches >= 3 and self.get_count(UnitTypeId.LAIR, include_pending=True):
            self.gas_buildings.to_count = min(2 * (hatches - 1), 8)
        if not self.flier_found:
            self.flier_found = self.enemy_fliers(self.knowledge)
        return await super().execute()

    def enemy_fliers(self, knowledge) -> bool:
        """
        Check enemy units to see if enough units are flying.

        Args:
            None
        Returns:
            bool: whether there's a flying unit
        """
        fly_counter = 0
        for unit in self.knowledge.known_enemy_units:
            if unit.type_id == UnitTypeId.BATTLECRUISER:
                return True
            if unit.is_flying and unit.can_attack:
                fly_counter += 1
                if fly_counter >= 4:
                    return True
        return False


class LarvaBuild(BuildOrder):
    """Manage Larva once opening is done."""

    def __init__(self):
        """Create orders to update."""
        self.hydra = ZergUnit(UnitTypeId.HYDRALISK, to_count=0)
        self.drone = ZergUnit(UnitTypeId.DRONE, to_count=0)
        self.zergling = ZergUnit(UnitTypeId.ZERGLING, to_count=0)
        self.roach = ZergUnit(UnitTypeId.ROACH, to_count=0)
        self.ravager = MorphRavager(target_count=0)
        self.swarmhost = ZergUnit(UnitTypeId.SWARMHOSTMP, to_count=0)
        self.inject_queen = ZergUnit(UnitTypeId.QUEEN, to_count=2, priority=True)

        super().__init__(
            [self.hydra, self.swarmhost, self.ravager, self.roach, self.drone, self.zergling, self.inject_queen]
        )

    async def execute(self):
        """Manage economy vs army."""
        # make sure the hard coded build order is done
        if self.get_count(UnitTypeId.HATCHERY, include_pending=True, include_killed=True) < 3:
            return await super().execute()

        # see if the enemy has flying units
        flying_enemy = self.enemy_fliers(self.knowledge)
        # build the main army
        # TODO: add the structures needed to build these units
        set_this_iteration = set()
        if self.knowledge.game_analyzer.our_army_predict not in at_least_small_disadvantage:
            self.drone.to_count = min(22 * self.get_count(UnitTypeId.HATCHERY), 80)
        else:
            self.drone.to_count = 0
        if self.cache.own(UnitTypeId.INFESTATIONPIT):
            self.swarmhost.to_count = 16
            set_this_iteration.add(self.swarmhost)
        if flying_enemy and self.cache.own(UnitTypeId.HYDRALISKDEN):
            self.hydra.to_count = 20
            self.swarmhost.to_count = 0
            set_this_iteration.add(self.hydra)
        if self.cache.own(UnitTypeId.ROACHWARREN):
            self.ravager.target_count = self.get_count(UnitTypeId.ROACH)
            self.roach.to_count = self.knowledge.available_gas / 25
            set_this_iteration.add(self.ravager)
            set_this_iteration.add(self.roach)
        else:
            if self.cache.own(UnitTypeId.SPAWNINGPOOL):
                self.zergling.to_count = 80
            set_this_iteration.add(self.zergling)
        self.set_to_zero(exclude=set_this_iteration)
        hatches = self.get_count(UnitTypeId.HATCHERY, include_pending=False, include_not_ready=False)
        if hatches >= 3:
            self.inject_queen.to_count = min(hatches, 5)

        return await super().execute()

    def set_to_zero(self, exclude: Set[ZergUnit] = set()) -> None:
        """
        If unit was not assigned this step, reset the count.
        Drones and queens are handled separately.
        """

        for unit_type in {
            self.hydra,
            self.zergling,
            self.roach,
            self.ravager,
            self.swarmhost,
        }:
            if unit_type not in exclude:
                unit_type.to_count = 0

    def enemy_fliers(self, knowledge) -> bool:
        """
        Check enemy units to see if enough units are flying.

        Args:
            None
        Returns:
            bool: whether there's a flying unit
        """
        fly_counter = 0
        for unit in self.knowledge.known_enemy_units:
            if unit.is_flying and unit.can_attack:
                fly_counter += 1
                if fly_counter >= 4:
                    return True
        return False


class PaulBot(KnowledgeBot):
    """Paul."""

    def __init__(self):
        """Set up attack parameters."""
        super().__init__("Paul")
        self.my_race = Race.Zerg
        self.attack = HostPlanZoneAttack(120)
        self.attack.retreat_multiplier = 0.3
        self.opener = None

    async def create_plan(self) -> BuildOrder:
        """Turn plan into BuildOrder."""
        attack_tactics = [
            PlanZoneGather(),
            PlanZoneDefense(),
            self.attack,
            PlanFinishEnemy(),
        ]

        if (
            self.knowledge.data_manager.last_result is not None
            and self.knowledge.data_manager.last_result.result == 1
            and self.knowledge.data_manager.last_result.build_used != ""
        ):
            build = self.knowledge.data_manager.last_result.build_used
        else:
            build = random.choice(["LingRush", "Macro", "12Pool"])

        self.knowledge.data_manager.set_build(build)

        self.opener = retrieve_build(build)

        if isinstance(self.opener, LingRush):
            return BuildOrder(
                [CounterTerranTie([self.opener]), PaulBuild(), InjectLarva(), attack_tactics, PlanWorkerOnlyDefense()]
            )
        else:
            return BuildOrder(
                [
                    self.opener,
                    CounterTerranTie([PaulBuild()]),
                    SequentialList(
                        [
                            InjectLarva(),
                            PlanDistributeWorkers(),
                            OverlordScout(),
                            PlanZoneGather(),
                            self.attack,
                            PlanZoneDefense(),
                            PlanFinishEnemy(),
                            PlanBurrowDrone(),
                            PlanWorkerOnlyDefense(),
                        ]
                    ),
                ]
            )

    async def on_upgrade_complete(self, upgrade):
        if upgrade == UpgradeId.ZERGLINGMOVEMENTSPEED:
            if isinstance(self.opener, LingRush):
                self.attack.start_attack_power = 1
                self.attack.attack_on_advantage = False
                self.attack.retreat_multiplier = 0


def main():
    """Run things."""
    sc2.run_game(
        sc2.maps.get("TritonLE"),
        [Bot(Race.Zerg, PaulBot()), Computer(Race.Terran, Difficulty.VeryHard)],
        realtime=False,
        save_replay_as="Paul1.SC2Replay",
    )


if __name__ == "__main__":
    main()
