"""Harass with Swarm Hosts using a Nydus."""
from sc2.position import Point2
from sharpy.plans.acts import ActBase


class NydusHostHarass(ActBase):
    """Create Worm and send units through and back."""

    def __init__(self, target: Point2):
        self.target = target

    async def execute(self):
        pass
