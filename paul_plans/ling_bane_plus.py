"""Ling Bane into Ultra/Mutalisks/Corruptors composition."""
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId

from paul_plans.mass_expand import MassExpand
from paul_plans.paul_auto_overlord import PaulAutoOverLord
from sharpy.plans import BuildOrder, SequentialList, Step, StepBuildGas
from sharpy.plans.acts import ActBuilding, Expand, Tech
from sharpy.plans.acts.zerg import MorphLair, ZergUnit, MorphHive
from sharpy.plans.require import All, UnitExists, TechReady
from sharpy.managers.game_states.advantage import at_least_clear_disadvantage


class LingBaneUltraCorruptor(BuildOrder):
    """Ling Bane into Ultralisks/Mutalisks/Corruptors."""

    def __init__(self):
        self.drone = ZergUnit(UnitTypeId.DRONE)
        self.queen = ZergUnit(UnitTypeId.QUEEN, to_count=3)
        self.zergling = ZergUnit(UnitTypeId.ZERGLING)
        self.baneling = ZergUnit(UnitTypeId.BANELING)
        self.ultra = ZergUnit(UnitTypeId.ULTRALISK, to_count=15)
        self.corruptor = ZergUnit(UnitTypeId.CORRUPTOR, to_count=40)
        self.mutalisk = ZergUnit(UnitTypeId.MUTALISK)
        self.overseer = ZergUnit(UnitTypeId.OVERSEER, to_count=3)

        build_units = BuildOrder(
            [
                Step(None, self.drone),
                Step(UnitExists(UnitTypeId.SPAWNINGPOOL), self.queen),
                Step(UnitExists(UnitTypeId.ULTRALISKCAVERN), self.ultra, skip_until=self.should_build_ultras),
                Step(UnitExists(UnitTypeId.SPIRE), self.corruptor, skip_until=self.should_build_air),
                Step(UnitExists(UnitTypeId.SPIRE), self.mutalisk, skip_until=self.should_build_air),
                Step(UnitExists(UnitTypeId.BANELINGNEST), self.baneling),
                Step(UnitExists(UnitTypeId.SPAWNINGPOOL), self.zergling),
                Step(
                    UnitExists(UnitTypeId.LAIR),
                    self.overseer,
                    skip_until=lambda k: k.enemy_units_manager.enemy_cloak_trigger,
                ),
            ]
        )

        tech_buildings = BuildOrder(
            Step(None, Expand(3, priority=True, consider_worker_production=False), skip_until=self.take_third),
            Step(None, StepBuildGas(to_count=2)),
            Step(UnitExists(UnitTypeId.LAIR), StepBuildGas(4)),
            Step(None, ActBuilding(UnitTypeId.SPAWNINGPOOL)),
            Step(UnitExists(UnitTypeId.SPAWNINGPOOL), ActBuilding(UnitTypeId.BANELINGNEST)),
            Step(UnitExists(UnitTypeId.BANELINGNEST), MorphLair()),
            Step(
                All([UnitExists(UnitTypeId.DRONE, 60), UnitExists(UnitTypeId.LAIR)]),
                ActBuilding(UnitTypeId.INFESTATIONPIT),
            ),
            Step(UnitExists(UnitTypeId.INFESTATIONPIT), StepBuildGas(6)),
            Step(UnitExists(UnitTypeId.LAIR), ActBuilding(UnitTypeId.EVOLUTIONCHAMBER, to_count=2)),
            Step(All([UnitExists(UnitTypeId.LAIR), UnitExists(UnitTypeId.INFESTATIONPIT)]), MorphHive()),
            Step(UnitExists(UnitTypeId.HIVE), ActBuilding(UnitTypeId.ULTRALISKCAVERN)),
            Step(UnitExists(UnitTypeId.LAIR), ActBuilding(UnitTypeId.SPIRE), skip_until=self.should_build_air),
            Step(UnitExists(UnitTypeId.HIVE), StepBuildGas(8))
        )

        upgrades = BuildOrder(
            Step(
                All([UnitExists(UnitTypeId.BANELINGNEST), UnitExists(UnitTypeId.LAIR)]),
                Tech(UpgradeId.CENTRIFICALHOOKS),
            ),
            SequentialList(
                Step(None, Tech(UpgradeId.ZERGMELEEWEAPONSLEVEL1)),
                Step(UnitExists(UnitTypeId.LAIR), Tech(UpgradeId.ZERGMELEEWEAPONSLEVEL2)),
                Step(UnitExists(UnitTypeId.HIVE), Tech(UpgradeId.ZERGMELEEWEAPONSLEVEL3)),
            ),
            SequentialList(
                Step(
                    UnitExists(UnitTypeId.EVOLUTIONCHAMBER, 2, include_not_ready=False, include_pending=False),
                    Tech(UpgradeId.ZERGGROUNDARMORSLEVEL1),
                ),
                Step(UnitExists(UnitTypeId.LAIR), Tech(UpgradeId.ZERGGROUNDARMORSLEVEL2)),
                Step(UnitExists(UnitTypeId.HIVE), Tech(UpgradeId.ZERGGROUNDARMORSLEVEL3)),
            ),
            Step(UnitExists(UnitTypeId.SPAWNINGPOOL), Tech(UpgradeId.ZERGLINGMOVEMENTSPEED)),
            Step(
                All([UnitExists(UnitTypeId.SPAWNINGPOOL), UnitExists(UnitTypeId.HIVE)]),
                Tech(UpgradeId.ZERGLINGATTACKSPEED),
            ),
            SequentialList(
                Step(UnitExists(UnitTypeId.ULTRALISKCAVERN), Tech(UpgradeId.CHITINOUSPLATING)),
                Step(UnitExists(UnitTypeId.ULTRALISKCAVERN), Tech(UpgradeId.ANABOLICSYNTHESIS)),
            ),
            SequentialList(
                Step(UnitExists(UnitTypeId.SPIRE), Tech(UpgradeId.ZERGFLYERWEAPONSLEVEL1)),
                Step(UnitExists(UnitTypeId.SPIRE), Tech(UpgradeId.ZERGFLYERWEAPONSLEVEL2)),
                Step(
                    All(
                        [
                            UnitExists(UnitTypeId.SPIRE),
                            UnitExists(UnitTypeId.HIVE),
                        ]
                    ),
                    Tech(UpgradeId.ZERGFLYERWEAPONSLEVEL3),
                ),
                Step(UnitExists(UnitTypeId.SPIRE), Tech(UpgradeId.ZERGFLYERARMORSLEVEL1)),
                Step(UnitExists(UnitTypeId.SPIRE), Tech(UpgradeId.ZERGFLYERARMORSLEVEL2)),
                Step(
                    All(
                        [
                            UnitExists(UnitTypeId.SPIRE),
                            UnitExists(UnitTypeId.HIVE),
                        ]
                    ),
                    Tech(UpgradeId.ZERGFLYERARMORSLEVEL3),
                ),
            ),
            Step(TechReady(UpgradeId.CENTRIFICALHOOKS), Tech(UpgradeId.OVERLORDSPEED)),
        )

        super().__init__([PaulAutoOverLord(), upgrades, tech_buildings, build_units, MassExpand()])

    def take_third(self, knowledge) -> bool:
        if self.knowledge.enemy_townhalls.amount >= 2:
            return True
        if self.knowledge.game_analyzer.our_army_advantage not in at_least_clear_disadvantage:
            return True
        return False

    def set_drones(self):
        safe = True
        for zone in self.knowledge.zone_manager.expansion_zones:
            if zone.is_ours and zone.is_under_attack:
                safe = False
        if safe:
            self.drone.to_count = min(
                85, max(60, self.get_count(UnitTypeId.HATCHERY) * 16 + self.get_count(UnitTypeId.EXTRACTOR) * 3)
            )
        else:
            self.drone.to_count = 0

    def should_build_air(self, knowledge):
        flier_found = False
        if self.knowledge.enemy_units_manager.enemy_total_power.air_power >= 1:
            # non_medivac_prism = False
            for unit in self.knowledge.known_enemy_units:
                if unit.is_flying and not flier_found:
                    flier_found = True
                # if unit.is_flying and unit.type_id not in {UnitTypeId.MEDIVAC, UnitTypeId.WARPPRISM}:
                if unit.is_flying:
                    # non_medivac_prism = True
                    # This one's my fault
                    # noinspection PyProtectedMember
                    self.corruptor.to_count = int(40 * self.knowledge.game_analyzer._enemy_air_percentage)
                    self.mutalisk.to_count = 0
                    break
            # if not non_medivac_prism:
            #     self.corruptor.to_count = 0
            #     # Also my fault
            #     # noinspection PyProtectedMember
            #     self.mutalisk.to_count = int(60 * self.knowledge.game_analyzer._enemy_air_percentage)
        return flier_found

    def should_build_ultras(self, knowledge):
        # Again, my fault
        # noinspection PyProtectedMember
        if self.knowledge.game_analyzer._enemy_air_percentage > .5:
            return False
        return True

    async def execute(self) -> bool:
        self.set_drones()

        self.queen.to_count = min(6, self.get_count(UnitTypeId.HATCHERY) + 3)

        if self.get_count(UnitTypeId.BANELINGNEST):
            self.baneling.to_count = self.cache.own(UnitTypeId.ZERGLING).amount // 2

        return await super().execute()
