from sc2.ids.unit_typeid import UnitTypeId
from sharpy.plans import BuildOrder

# from sharpy.plans.acts.zerg import ZergExpand
from sharpy.plans.acts import ActExpand


class MassExpand(BuildOrder):
    """Continuously expand if a mineral threshold is reached."""

    def __init__(self):
        self.expander = ActExpand(to_count=0, priority=True)
        super().__init__([self.expander])

    async def execute(self):
        if self.ai.minerals >= 700:
            current_bases = self.get_count(UnitTypeId.HATCHERY)
            self.expander.to_count = current_bases + 1
        return await super().execute()
