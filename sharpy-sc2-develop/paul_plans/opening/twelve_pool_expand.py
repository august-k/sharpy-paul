"""12 Pool Macro opening."""

from sc2.ids.unit_typeid import UnitTypeId

from sharpy.plans import BuildOrder, SequentialList, Step
from sharpy.plans.acts import ActBuilding
from sharpy.plans.acts.zerg import ZergExpand, ZergUnit
from sharpy.plans.require import RequiredSupply, RequiredUnitReady


class TwelvePoolExpand(BuildOrder):
    """
    Gasless 12 Pool into Expansion

    Macro Build
    """

    def __init__(self):
        """Build order steps to be combined."""
        opening = SequentialList(
            Step(None, ActBuilding(UnitTypeId.SPAWNINGPOOL)),
            Step(None, ZergUnit(UnitTypeId.DRONE, to_count=14)),
            Step(RequiredSupply(14), ZergUnit(UnitTypeId.OVERLORD, to_count=2, only_once=True)),
            Step(RequiredUnitReady(UnitTypeId.SPAWNINGPOOL, 1), ZergUnit(UnitTypeId.ZERGLING, 6, only_once=True)),
            ZergExpand(2),
            Step(
                RequiredUnitReady(UnitTypeId.SPAWNINGPOOL), ZergUnit(UnitTypeId.ZERGLING, to_count=12, only_once=True)
            ),
        )

        super().__init__([opening])
