"""Ling Bane into Ultra composition."""
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId

from paul_plans.mass_expand import MassExpand
from sharpy.plans import BuildOrder, SequentialList, Step, StepBuildGas
from sharpy.plans.acts import ActBuilding, ActTech
from sharpy.plans.acts.zerg import AutoOverLord, MorphLair, ZergUnit, MorphHive
from sharpy.plans.require import RequiredAll, UnitExists, RequiredTime


class LingBaneUltra(BuildOrder):
    """Ling Bane into Ultralisks."""

    def __init__(self):
        self.drone = ZergUnit(UnitTypeId.DRONE)
        self.queen = ZergUnit(UnitTypeId.QUEEN, to_count=3)
        self.zergling = ZergUnit(UnitTypeId.ZERGLING)
        self.baneling = ZergUnit(UnitTypeId.BANELING)
        self.ultra = ZergUnit(UnitTypeId.ULTRALISK, to_count=15)
        self.overseer = ZergUnit(UnitTypeId.OVERSEER, to_count=3)

        build_units = BuildOrder(
            [
                Step(None, self.drone),
                Step(UnitExists(UnitTypeId.SPAWNINGPOOL), self.queen),
                Step(UnitExists(UnitTypeId.ULTRALISKCAVERN), self.ultra),
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
            Step(None, StepBuildGas(to_count=2)),
            Step(UnitExists(UnitTypeId.LAIR), StepBuildGas(4)),
            Step(None, ActBuilding(UnitTypeId.SPAWNINGPOOL)),
            Step(UnitExists(UnitTypeId.SPAWNINGPOOL), ActBuilding(UnitTypeId.BANELINGNEST)),
            Step(RequiredTime(5.5 * 60), MorphLair()),
            Step(
                RequiredAll([UnitExists(UnitTypeId.DRONE, 60), UnitExists(UnitTypeId.LAIR)]),
                ActBuilding(UnitTypeId.INFESTATIONPIT),
            ),
            Step(UnitExists(UnitTypeId.INFESTATIONPIT), StepBuildGas(6)),
            Step(UnitExists(UnitTypeId.LAIR), ActBuilding(UnitTypeId.EVOLUTIONCHAMBER, to_count=2)),
            Step(RequiredAll([UnitExists(UnitTypeId.LAIR), UnitExists(UnitTypeId.INFESTATIONPIT)]), MorphHive()),
            Step(UnitExists(UnitTypeId.HIVE), ActBuilding(UnitTypeId.ULTRALISKCAVERN)),
            Step(UnitExists(UnitTypeId.HIVE), StepBuildGas(8))
        )

        upgrades = BuildOrder(
            Step(
                RequiredAll([UnitExists(UnitTypeId.BANELINGNEST), UnitExists(UnitTypeId.LAIR),]),
                ActTech(UpgradeId.CENTRIFICALHOOKS),
            ),
            SequentialList(
                Step(None, ActTech(UpgradeId.ZERGMELEEWEAPONSLEVEL1)),
                Step(UnitExists(UnitTypeId.LAIR), ActTech(UpgradeId.ZERGMELEEWEAPONSLEVEL2)),
                Step(UnitExists(UnitTypeId.HIVE), ActTech(UpgradeId.ZERGMELEEWEAPONSLEVEL3)),
            ),
            SequentialList(
                Step(
                    UnitExists(UnitTypeId.EVOLUTIONCHAMBER, 2, include_not_ready=False, include_pending=False),
                    ActTech(UpgradeId.ZERGGROUNDARMORSLEVEL1),
                ),
                Step(UnitExists(UnitTypeId.LAIR), ActTech(UpgradeId.ZERGGROUNDARMORSLEVEL2)),
                Step(UnitExists(UnitTypeId.HIVE), ActTech(UpgradeId.ZERGGROUNDARMORSLEVEL3)),
            ),
            Step(UnitExists(UnitTypeId.SPAWNINGPOOL), ActTech(UpgradeId.ZERGLINGMOVEMENTSPEED)),
            Step(
                RequiredAll([UnitExists(UnitTypeId.SPAWNINGPOOL), UnitExists(UnitTypeId.HIVE)]),
                ActTech(UpgradeId.ZERGLINGATTACKSPEED),
            ),
            SequentialList(
                Step(UnitExists(UnitTypeId.ULTRALISKCAVERN), ActTech(UpgradeId.CHITINOUSPLATING)),
                Step(UnitExists(UnitTypeId.ULTRALISKCAVERN), ActTech(UpgradeId.ANABOLICSYNTHESIS)),
            ),
        )

        super().__init__([upgrades, tech_buildings, build_units, MassExpand(), AutoOverLord()])

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

    async def execute(self) -> bool:
        self.set_drones()

        self.queen.to_count = min(6, self.get_count(UnitTypeId.HATCHERY) + 3)

        if self.get_count(UnitTypeId.BANELINGNEST):
            self.baneling.to_count = self.cache.own(UnitTypeId.ZERGLING).amount // 2

        return await super().execute()
