"""Adaptaion of ViBE's Plat to Master build."""
from sc2.ids.unit_typeid import UnitTypeId
from sharpy.plans import BuildOrder, SequentialList, Step, StepBuildGas
from sharpy.plans.acts.zerg import ZergUnit
from sharpy.plans.acts import ActExpand, ActBuilding
from sharpy.plans.require import UnitExists, RequiredUnitReady


class ViBE(BuildOrder):
    """ViBE's Plat to Master Build. 17 hatch, 18 pool, 20 gas into roaches."""

    def __init__(self):
        """Create the build order."""
        opener = SequentialList(
            Step(None, ZergUnit(UnitTypeId.DRONE, to_count=13)),
            Step(None, ZergUnit(UnitTypeId.OVERLORD, to_count=2)),
            Step(None, ZergUnit(UnitTypeId.DRONE, to_count=17)),
            Step(None, ActExpand(2, priority=True, consider_worker_production=False)),
            Step(
                UnitExists(UnitTypeId.HATCHERY, count=2, include_pending=True, include_not_ready=True),
                ZergUnit(UnitTypeId.DRONE, to_count=18),
            ),
            Step(None, ActBuilding(UnitTypeId.SPAWNINGPOOL)),
            Step(None, ZergUnit(UnitTypeId.DRONE, to_count=20)),
            StepBuildGas(1),
            Step(RequiredUnitReady(UnitTypeId.SPAWNINGPOOL), ZergUnit(UnitTypeId.QUEEN, 2)),
            Step(RequiredUnitReady(UnitTypeId.SPAWNINGPOOL), ZergUnit(UnitTypeId.ZERGLING, 6)),
            Step(None, ZergUnit(UnitTypeId.OVERLORD, to_count=3)),
            # end of build hard order, switch to reactive play
        )
        super().__init__(opener)
