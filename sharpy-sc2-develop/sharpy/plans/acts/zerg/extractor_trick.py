from sharpy.plans.acts import ActBase

from sc2.unit import Unit
from sc2.ids.unit_typeid import UnitTypeId


class ExtractorTrick(ActBase):
    def __init__(self):
        super().__init__()
        self.trick_done = False
        self.best_gas: Unit = None

    async def find_gas(self):
        for townhall in self.ai.townhalls:  # type: Unit
            if not townhall.is_ready or townhall.build_progress < 0.9:
                # Only build gas for bases that are almost finished
                continue

            for geyser in self.ai.vespene_geyser.closer_than(
                15, townhall
            ):  # type: Unit
                exists = False
                for harvester in harvesters:  # type: Unit
                    if harvester.position.distance_to(geyser.position) <= 1:
                        exists = True
                        break
                if not exists:
                    score = geyser.vespene_contents
                    if score > best_score:
                        self.best_gas = geyser

    @abstractmethod
    async def execute(self) -> bool:
        """Return True when the act is complete and execution can continue to the next act.
        Return False if you want to block execution and not continue to the next act."""
        if self.trick_done:
            return True

        worker = self.knowledge.roles.free_workers

        if not self.best_gas:
            self.find_gas
        self.ai.do(worker.build(UnitTypeId.EXTRACTOR,))
