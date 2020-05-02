"""Paul's macro opening."""
from typing import TYPE_CHECKING
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId

from sharpy.plans import BuildOrder, SequentialList, Step, StepBuildGas
from sharpy.plans.acts import ActExpand, ActBuilding, ActTech
from sharpy.plans.acts.zerg import ZergUnit
from sharpy.plans.require import RequiredAll, UnitExists, RequiredGas

if TYPE_CHECKING:
    from sharpy.knowledges import Knowledge


class MacroBuild(BuildOrder):
    """
    Macro Opener for Paul.

    Three hatch with ling speed.
    """

    def __init__(self):
        """Build order steps to be combined."""
        self.done = False
        opening = SequentialList(
            [
                Step(None, ZergUnit(UnitTypeId.DRONE, to_count=13, only_once=True)),
                Step(None, ZergUnit(UnitTypeId.OVERLORD, to_count=2, only_once=True)),
                Step(None, ZergUnit(UnitTypeId.DRONE, to_count=17)),
                Step(None, ActExpand(2, priority=True, consider_worker_production=False)),
                Step(None, ZergUnit(UnitTypeId.DRONE, to_count=18, only_once=True)),
                Step(None, StepBuildGas(to_count=1)),
                Step(
                    UnitExists(
                        UnitTypeId.EXTRACTOR,
                        count=1,
                        include_pending=True,
                        include_not_ready=True,
                    ),
                    ActBuilding(UnitTypeId.SPAWNINGPOOL),
                ),
                Step(
                    UnitExists(
                        UnitTypeId.SPAWNINGPOOL,
                        count=1,
                        include_not_ready=True,
                        include_pending=True,
                    ),
                    ZergUnit(UnitTypeId.DRONE, to_count=20),
                ),
                Step(
                    UnitExists(UnitTypeId.SPAWNINGPOOL),
                    ZergUnit(UnitTypeId.ZERGLING, to_count=6),
                ),
                Step(
                    UnitExists(UnitTypeId.SPAWNINGPOOL),
                    ZergUnit(UnitTypeId.QUEEN, to_count=2),
                ),
                Step(None, ActExpand(3, priority=True, consider_worker_production=False)),
            ]
        )
        ling_speed = BuildOrder(
            [
                Step(
                    RequiredAll(
                        [UnitExists(UnitTypeId.SPAWNINGPOOL), RequiredGas(100)]
                    ),
                    ActTech(UpgradeId.ZERGLINGMOVEMENTSPEED, UnitTypeId.SPAWNINGPOOL),
                )
            ]
        )
        super().__init__([opening, ling_speed])

    async def start(self, knowledge: "Knowledge"):
        await super().start(knowledge)
        for order in self.orders:
            await order.start(knowledge)

    async def execute(self) -> bool:
        if self.get_count(UnitTypeId.HATCHERY) >= 3:
            self.done = True
        result = True
        for order in self.orders:
            if not await order.execute():
                result = False

        return result
