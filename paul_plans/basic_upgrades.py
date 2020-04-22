"""Basic upgrade BuildOrder."""

from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sharpy.plans import SequentialList, Step, BuildOrder
from sharpy.plans.require import UnitExists, RequiredAll, RequiredTechReady, RequiredUnitReady
from sharpy.plans.acts import ActTech
from sharpy.plans.acts.zerg import MorphHive


class StandardUpgrades(BuildOrder):
    """Ranged > Carapace > Melee assuming double evo chamber."""

    def __init__(self):
        """Research basic unit upgrades with Overlord Speed and Burrow."""
        upgrades = BuildOrder(
            [
                # ranged upgrades
                SequentialList(
                    Step(
                        RequiredUnitReady(UnitTypeId.EVOLUTIONCHAMBER),
                        ActTech(UpgradeId.ZERGMISSILEWEAPONSLEVEL1, UnitTypeId.EVOLUTIONCHAMBER),
                    ),
                    Step(
                        RequiredAll(
                            [
                                RequiredUnitReady(UnitTypeId.EVOLUTIONCHAMBER),
                                RequiredTechReady(UpgradeId.ZERGMISSILEWEAPONSLEVEL1),
                                UnitExists(UnitTypeId.LAIR),
                            ]
                        ),
                        ActTech(UpgradeId.ZERGMISSILEWEAPONSLEVEL2, UnitTypeId.EVOLUTIONCHAMBER),
                    ),
                    Step(
                        RequiredAll(
                            [
                                RequiredUnitReady(UnitTypeId.EVOLUTIONCHAMBER),
                                RequiredTechReady(UpgradeId.ZERGMISSILEWEAPONSLEVEL2),
                                UnitExists(UnitTypeId.HIVE),
                            ]
                        ),
                        ActTech(UpgradeId.ZERGMISSILEWEAPONSLEVEL3, UnitTypeId.EVOLUTIONCHAMBER),
                    ),
                ),
                # ground carapace upgrades
                SequentialList(
                    Step(
                        RequiredUnitReady(UnitTypeId.EVOLUTIONCHAMBER),
                        ActTech(UpgradeId.ZERGGROUNDARMORSLEVEL1, UnitTypeId.EVOLUTIONCHAMBER),
                    ),
                    Step(
                        RequiredAll(
                            [
                                RequiredUnitReady(UnitTypeId.EVOLUTIONCHAMBER),
                                RequiredTechReady(UpgradeId.ZERGGROUNDARMORSLEVEL1),
                                UnitExists(UnitTypeId.LAIR),
                            ]
                        ),
                        ActTech(UpgradeId.ZERGGROUNDARMORSLEVEL2, UnitTypeId.EVOLUTIONCHAMBER),
                    ),
                    Step(
                        RequiredAll(
                            [
                                RequiredUnitReady(UnitTypeId.EVOLUTIONCHAMBER),
                                RequiredTechReady(UpgradeId.ZERGGROUNDARMORSLEVEL2),
                                UnitExists(UnitTypeId.HIVE),
                            ]
                        ),
                        ActTech(UpgradeId.ZERGGROUNDARMORSLEVEL3, UnitTypeId.EVOLUTIONCHAMBER),
                    ),
                ),
                # melee upgrades
                SequentialList(
                    Step(
                        RequiredUnitReady(UnitTypeId.EVOLUTIONCHAMBER),
                        ActTech(UpgradeId.ZERGMELEEWEAPONSLEVEL1, UnitTypeId.EVOLUTIONCHAMBER),
                    ),
                    Step(
                        RequiredAll(
                            [
                                RequiredUnitReady(UnitTypeId.EVOLUTIONCHAMBER),
                                RequiredTechReady(UpgradeId.ZERGMELEEWEAPONSLEVEL1),
                                UnitExists(UnitTypeId.LAIR),
                            ]
                        ),
                        ActTech(UpgradeId.ZERGMELEEWEAPONSLEVEL2, UnitTypeId.EVOLUTIONCHAMBER),
                    ),
                    Step(
                        RequiredAll(
                            [
                                RequiredUnitReady(UnitTypeId.EVOLUTIONCHAMBER),
                                RequiredTechReady(UpgradeId.ZERGMELEEWEAPONSLEVEL2),
                                UnitExists(UnitTypeId.HIVE),
                            ]
                        ),
                        ActTech(UpgradeId.ZERGMELEEWEAPONSLEVEL3, UnitTypeId.EVOLUTIONCHAMBER),
                    ),
                ),
                # overlord speed then burrow
                SequentialList(
                    Step(UnitExists(UnitTypeId.QUEEN, 2), ActTech(UpgradeId.OVERLORDSPEED, UnitTypeId.HATCHERY)),
                    Step(UnitExists(UnitTypeId.LAIR), ActTech(UpgradeId.BURROW, UnitTypeId.LAIR)),
                ),
                Step(
                    RequiredAll(
                        [
                            UnitExists(UnitTypeId.INFESTATIONPIT),
                            RequiredUnitReady(UnitTypeId.LAIR),
                            RequiredTechReady(UpgradeId.ZERGMISSILEWEAPONSLEVEL2),
                        ]
                    ),
                    MorphHive(),
                ),
            ]
        )
        super().__init__([upgrades])
