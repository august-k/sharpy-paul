from typing import Dict, List
from sharpy.plans.acts import ActBase, ActBuilding
from sharpy.plans.acts.zerg import MorphLair, ZergUnit
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.units import Units
from sharpy.knowledges import Knowledge
from sharpy.managers.roles import UnitTask
from sharpy.managers.combat2 import MicroRules, MoveType
from paul_plans.suicide_ling_micro import SuicideLingMicro


class NydusMain(ActBase):
    """Set up Nydus in their main."""

    units: Units

    def __init__(self, unit_type: UnitTypeId, amount: int):
        super().__init__()
        self.micro = MicroRules()
        self.micro.load_default_methods()
        self.micro.unit_micros[UnitTypeId.ZERGLING] = SuicideLingMicro()
        self.started = False
        self.ended = False
        self.unit_type = unit_type
        self.amount = amount
        self.lair_tech = MorphLair()
        self.network = ActBuilding(UnitTypeId.NYDUSNETWORK, to_count=1)
        self.zerg_build = ZergUnit(unit_type)
        self.tags: List[int] = []

    async def start(self, knowledge: "Knowledge"):
        await super(NydusMain, self).start(knowledge)
        await self.lair_tech.start(knowledge)
        await self.network.start(knowledge)
        await self.zerg_build.start(knowledge)
        await self.micro.start(knowledge)
        self.units = Units([], self.ai)

    async def execute(self) -> bool:
        if self.cache.own(UnitTypeId.NYDUSCANAL).ready:
            for canal in self.cache.own(UnitTypeId.NYDUSCANAL).ready:
                self.do(canal(AbilityId.UNLOADALL_NYDUSWORM))

        if self.knowledge.lost_units_manager.own_lost_type(UnitTypeId.NYDUSCANAL):
            self.ended = True

        if self.ended:
            return True

        if self.cache.own(self.unit_type).amount < self.amount:
            self.zerg_build.to_count = self.amount
            await self.zerg_build.execute()

        self.units.clear()

        if not self.get_count(UnitTypeId.LAIR, include_pending=True, include_not_ready=True) + self.get_count(
            UnitTypeId.HIVE
        ):
            await self.lair_tech.execute()
            return True

        if not self.get_count(UnitTypeId.NYDUSNETWORK, include_pending=True, include_not_ready=True):
            await self.network.execute()
            return True

        # build the nydus worm
        if not self.get_count(UnitTypeId.NYDUSCANAL) and self.get_count(
            UnitTypeId.NYDUSNETWORK, include_not_ready=False, include_pending=False
        ):
            closest_overlord = self.cache.own(UnitTypeId.OVERLORD).closest_to(self.knowledge.enemy_start_location)
            nydus_network = self.cache.own(UnitTypeId.NYDUSNETWORK).first
            for i in range(11):
                pos = closest_overlord.position.towards(self.knowledge.enemy_start_location, i)
                if self.ai.get_terrain_z_height(pos) != self.ai.get_terrain_z_height(
                    self.knowledge.enemy_start_location
                ):
                    continue
                if self.ai.is_visible(pos) and await self.ai.can_place(UnitTypeId.NYDUSCANAL, pos):
                    self.do(nydus_network(AbilityId.BUILD_NYDUSWORM, pos))
            if i == 10 and not nydus_network.orders:
                self.do(closest_overlord.move(closest_overlord.position.towards(pos, 1)))

        # put units into the Nydus
        if self.get_count(UnitTypeId.NYDUSCANAL, include_pending=True, include_not_ready=True) and self.get_count(
            UnitTypeId.NYDUSNETWORK, include_pending=False, include_not_ready=False
        ):
            network = self.cache.own(UnitTypeId.NYDUSNETWORK).first
            if not self.started:
                free_units = self.roles.get_types_from(
                    {self.unit_type}, UnitTask.Idle, UnitTask.Moving, UnitTask.Gathering
                )
                if free_units.amount < self.amount:
                    return True
                self.units.extend(free_units.random_group_of(self.amount))
                self.tags = self.units.tags
                self.started = True
            else:
                unit_grouping = self.roles.get_types_from({self.unit_type}, UnitTask.Reserved)
                self.units.extend(unit_grouping.tags_in(self.tags))
                if not self.units:
                    self.ended = True
                    return True

        if self.units:
            network = None
            canal = None
            if self.get_count(UnitTypeId.NYDUSNETWORK):
                network = self.cache.own(UnitTypeId.NYDUSNETWORK).first
            if self.get_count(UnitTypeId.NYDUSCANAL):
                canal = self.cache.own(UnitTypeId.NYDUSCANAL).first
            if not canal or not network:
                return True
            self.roles.set_tasks(UnitTask.Reserved, self.units)
            for unit in self.units:
                if unit.distance_to(canal) <= unit.distance_to(network):
                    self.combat.add_unit(unit)
                else:
                    self.do(network(AbilityId.LOAD_NYDUSNETWORK, unit))
            self.combat.execute(
                self.knowledge.enemy_expansion_zones[0].center_location, MoveType.Assault, rules=self.micro
            )

        return True  # never block
