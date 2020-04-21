"""15 hatch, 14 gas, 14 pool ling flood."""

from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId

from sharpy.plans import BuildOrder, SequentialList, Step, StepBuildGas
from sharpy.plans.acts import ActTech, ActBuilding
from sharpy.plans.acts.zerg import ZergUnit, AutoOverLord
from sharpy.plans.acts import CancelBuilding, ActExpand
from sharpy.plans.require import (
    RequiredUnitExists,
    RequiredSupply,
    RequiredAll,
    RequiredGas,
    RequiredMinerals,
    RequiredTechReady,
    RequiredAny,
)
from sharpy.plans.tactics import PlanDistributeWorkers


class LingRush(BuildOrder):
    """
    Original Ling Rush for Paul.

    15 hatch/14 gas/14 pool > ling flood. No transition intended.
    """

    def __init__(self):
        """Build order steps to be combined."""
        extractor_trick = SequentialList(
            [
                Step(
                    RequiredSupply(14),
                    StepBuildGas(1),
                    skip=RequiredUnitExists(UnitTypeId.EXTRACTOR, include_killed=True, include_pending=True),
                ),
                Step(
                    RequiredUnitExists(UnitTypeId.EXTRACTOR, 1, include_pending=True, include_not_ready=True,),
                    ZergUnit(UnitTypeId.DRONE, to_count=14),
                ),
                # SequentialList will take care of making sure the drone was made
                Step(
                    RequiredUnitExists(UnitTypeId.EXTRACTOR),
                    CancelBuilding(UnitTypeId.EXTRACTOR, to_count=0),
                    skip=RequiredUnitExists(UnitTypeId.EXTRACTOR, 1, include_killed=True, include_not_ready=False,),
                ),
            ]
        )

        opening = SequentialList(
            [
                Step(None, ZergUnit(UnitTypeId.DRONE, to_count=14)),
                Step(
                    RequiredSupply(14),
                    extractor_trick,
                    skip=RequiredUnitExists(UnitTypeId.EXTRACTOR, 1, include_killed=True, include_not_ready=False,),
                ),
                ActExpand(2, priority=True, consider_worker_production=False),
                Step(RequiredAll([RequiredSupply(14), RequiredMinerals(130)]), StepBuildGas(1),),
                Step(None, ZergUnit(UnitTypeId.DRONE, to_count=14)),
                Step(RequiredSupply(14), ActBuilding(UnitTypeId.SPAWNINGPOOL)),
                Step(
                    RequiredAll([RequiredUnitExists(UnitTypeId.HATCHERY), RequiredUnitExists(UnitTypeId.SPAWNINGPOOL)]),
                    ZergUnit(UnitTypeId.QUEEN, 2),
                ),
                # spam lings
                Step(RequiredUnitExists(UnitTypeId.SPAWNINGPOOL), ZergUnit(UnitTypeId.ZERGLING, 999)),
            ]
        )

        ling_speed = BuildOrder(
            [
                Step(
                    RequiredAll([RequiredUnitExists(UnitTypeId.SPAWNINGPOOL), RequiredGas(100)]),
                    ActTech(UpgradeId.ZERGLINGMOVEMENTSPEED, UnitTypeId.SPAWNINGPOOL),
                )
            ]
        )

        worker_distribution = SequentialList(
            [
                Step(
                    RequiredSupply(15),
                    PlanDistributeWorkers(),
                    skip=RequiredUnitExists(UnitTypeId.HATCHERY, 2, include_killed=True,),
                ),
                Step(
                    RequiredUnitExists(UnitTypeId.EXTRACTOR),
                    PlanDistributeWorkers(min_gas=3),
                    skip=RequiredAny(
                        [RequiredTechReady(UpgradeId.ZERGLINGMOVEMENTSPEED, percentage=0.01), RequiredGas(96)]
                    ),
                ),
                Step(
                    RequiredAny([RequiredTechReady(UpgradeId.ZERGLINGMOVEMENTSPEED, percentage=0.01), RequiredGas(96)]),
                    PlanDistributeWorkers(max_gas=0),
                ),
            ]
        )

        overlords = BuildOrder([Step(None, AutoOverLord(), skip_until=RequiredUnitExists(UnitTypeId.SPAWNINGPOOL),)])

        super().__init__([opening, ling_speed, worker_distribution, overlords])
