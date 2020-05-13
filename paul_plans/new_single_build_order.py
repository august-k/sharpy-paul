from typing import TYPE_CHECKING
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sharpy.plans import BuildOrder, StepBuildGas, Step, SequentialList
from sharpy.plans.acts import ActBuilding, ActExpand, ActTech
from sharpy.plans.acts.zerg import ZergUnit, AutoOverLord
from sharpy.plans.tactics import PlanDistributeWorkers
from sharpy.plans.tactics.zerg import InjectLarva, SpreadCreep
from sharpy.plans.require import RequiredAll, RequiredGas, RequiredMinerals, UnitExists

from paul_plans.scout_manager import EnemyBuild
from paul_plans.roach_rush_response import RoachRushResponse

if TYPE_CHECKING:
    from sharpy.knowledges import Knowledge


class PaulBuild(BuildOrder):
    """Build for Paul."""

    def __init__(self):
        """Set everything up."""
        self.enemy_rushes = {
            EnemyBuild.GeneralRush,
            EnemyBuild.Pool12,
            EnemyBuild.RoachRush,
            EnemyBuild.LingRush,
            EnemyBuild.CannonRush,
            EnemyBuild.EarlyMarines,
        }
        self.distribute = PlanDistributeWorkers()

        # basic build (17, 18, 17)
        base_build = SequentialList(
            [
                Step(None, ZergUnit(UnitTypeId.DRONE, to_count=13)),
                Step(None, ZergUnit(UnitTypeId.OVERLORD, to_count=2)),
                Step(None, ZergUnit(UnitTypeId.DRONE, to_count=17)),
                Step(None, ActExpand(to_count=2, priority=True, consider_worker_production=False)),
                Step(None, ZergUnit(UnitTypeId.DRONE, to_count=18)),
                Step(RequiredMinerals(120), StepBuildGas(to_count=1)),
                Step(None, ActBuilding(UnitTypeId.SPAWNINGPOOL)),
                Step(None, ZergUnit(UnitTypeId.DRONE, to_count=20)),
                Step(UnitExists(UnitTypeId.SPAWNINGPOOL), ZergUnit(UnitTypeId.ZERGLING, to_count=6)),
                Step(UnitExists(UnitTypeId.SPAWNINGPOOL), ZergUnit(UnitTypeId.QUEEN, to_count=2)),
                Step(
                    RequiredAll([UnitExists(UnitTypeId.SPAWNINGPOOL), RequiredGas(100)]),
                    ActTech(UpgradeId.ZERGLINGMOVEMENTSPEED),
                ),
                Step(UnitExists(UnitTypeId.SPAWNINGPOOL), ZergUnit(UnitTypeId.ZERGLING, to_count=100)),
            ]
        )

        build_together = BuildOrder(
            [
                Step(None, base_build, skip=lambda k: k.ai.scout_manager.enemy_build in self.enemy_rushes),
                Step(None, RoachRushResponse(), skip=lambda k: k.ai.scout_manager.enemy_build != EnemyBuild.RoachRush),
            ]
        )

        super().__init__(build_together, self.distribute, AutoOverLord(), InjectLarva(), SpreadCreep())
