from sharpy.plans import BuildOrder, SequentialList, Step
from sharpy.plans.tactics.zerg import OverlordScoutMain
from sharpy.plans.require import RequiredTime


class OverlordScoutOrder(BuildOrder):
    """Check main every two minutes until 30 minutes."""

    def __init__(self):
        scout_pattern = SequentialList(
            Step(None, OverlordScoutMain(), skip_until=RequiredTime(4 * 60)),
            Step(None, OverlordScoutMain(), skip_until=RequiredTime(6 * 60)),
            Step(None, OverlordScoutMain(), skip_until=RequiredTime(8 * 60)),
            Step(None, OverlordScoutMain(), skip_until=RequiredTime(10 * 60)),
            Step(None, OverlordScoutMain(), skip_until=RequiredTime(12 * 60)),
            Step(None, OverlordScoutMain(), skip_until=RequiredTime(14 * 60)),
            Step(None, OverlordScoutMain(), skip_until=RequiredTime(16 * 60)),
            Step(None, OverlordScoutMain(), skip_until=RequiredTime(18 * 60)),
            Step(None, OverlordScoutMain(), skip_until=RequiredTime(20 * 60)),
            Step(None, OverlordScoutMain(), skip_until=RequiredTime(22 * 60)),
            Step(None, OverlordScoutMain(), skip_until=RequiredTime(24 * 60)),
            Step(None, OverlordScoutMain(), skip_until=RequiredTime(26 * 60)),
            Step(None, OverlordScoutMain(), skip_until=RequiredTime(28 * 60)),
            Step(None, OverlordScoutMain(), skip_until=RequiredTime(30 * 60)),
        )

        super().__init__([scout_pattern])
