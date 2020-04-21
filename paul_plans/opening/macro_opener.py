"""Paul's macro opening."""

from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId

from sharpy.plans import BuildOrder, SequentialList, Step, StepBuildGas
from sharpy.plans.acts import ActExpand, ActBuilding, ActTech
from sharpy.plans.acts.zerg import ZergUnit
from sharpy.plans.require import RequiredAll, RequiredUnitExists, RequiredGas


class MacroBuild(BuildOrder):
    """
    Macro Opener for Paul.

    Three hatch with ling speed.
    """

    def __init__(self):
        """Build order steps to be combined."""
        opening = SequentialList(
            [
                Step(None, ZergUnit(UnitTypeId.DRONE, to_count=13, only_once=True)),
                Step(None, ZergUnit(UnitTypeId.OVERLORD, to_count=2, only_once=True)),
                Step(None, ZergUnit(UnitTypeId.DRONE, to_count=17)),
                Step(None, ActExpand(2)),
                Step(None, ZergUnit(UnitTypeId.DRONE, to_count=18, only_once=True)),
                Step(None, StepBuildGas(to_count=1)),
                Step(
                    RequiredUnitExists(
                        UnitTypeId.EXTRACTOR,
                        count=1,
                        include_pending=True,
                        include_not_ready=True,
                    ),
                    ActBuilding(UnitTypeId.SPAWNINGPOOL),
                ),
                Step(
                    RequiredUnitExists(
                        UnitTypeId.SPAWNINGPOOL,
                        count=1,
                        include_not_ready=True,
                        include_pending=True,
                    ),
                    ZergUnit(UnitTypeId.DRONE, to_count=21),
                ),
                Step(
                    RequiredUnitExists(UnitTypeId.SPAWNINGPOOL),
                    ZergUnit(UnitTypeId.ZERGLING, to_count=6),
                ),
                Step(
                    RequiredUnitExists(UnitTypeId.SPAWNINGPOOL),
                    ZergUnit(UnitTypeId.QUEEN, to_count=2),
                ),
                Step(None, ActExpand(3)),
            ]
        )
        ling_speed = BuildOrder(
            [
                Step(
                    RequiredAll(
                        [RequiredUnitExists(UnitTypeId.SPAWNINGPOOL), RequiredGas(100)]
                    ),
                    ActTech(UpgradeId.ZERGLINGMOVEMENTSPEED, UnitTypeId.SPAWNINGPOOL),
                )
            ]
        )
        super().__init__([opening, ling_speed])
