"""Build order for Paul as a single BuildOrder"""
from typing import TYPE_CHECKING

from paul_plans.defensive_building import DefensiveBuilding, DefensePosition
from paul_plans.basic_upgrades import StandardUpgrades
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.player import Race
from sharpy.plans import BuildOrder, Step, SequentialList, StepBuildGas
from sharpy.plans.acts import ActExpand, ActBuilding, ActTech
from sharpy.plans.acts.zerg import ZergUnit, AutoOverLord, MorphLair
from sharpy.plans.require import RequiredMinerals, UnitExists, RequiredAll, RequiredTechReady, RequiredTime
from sharpy.plans.tactics import PlanDistributeWorkers
from sharpy.plans.tactics.zerg import OverlordScout, LingScout
from sharpy.plans.tactics.scouting import ScoutLocation
from paul_plans.roach_rush_response import RoachRushResponse
from paul_plans.scout_manager import EnemyBuild

if TYPE_CHECKING:
    from sharpy.knowledges import Knowledge


class PaulBuild(BuildOrder):
    """Determine what to build."""

    enemy_rush = False

    def __init__(self):
        self.enemy_nat_scouted = False
        self.enemy_rushes = {
            EnemyBuild.GeneralRush,
            EnemyBuild.Pool12,
            EnemyBuild.RoachRush,
            EnemyBuild.LingRush,
            EnemyBuild.CannonRush,
            EnemyBuild.EarlyMarines,
            EnemyBuild.BCRush,
        }

        self.drones = ZergUnit(UnitTypeId.DRONE, to_count=0)
        self.lings = ZergUnit(UnitTypeId.ZERGLING, to_count=0)
        self.banelings = ZergUnit(UnitTypeId.BANELING, to_count=0)
        self.queens = ZergUnit(UnitTypeId.QUEEN, to_count=0)
        self.roaches = ZergUnit(UnitTypeId.ROACH, to_count=0)
        self.ravagers = ZergUnit(UnitTypeId.RAVAGER, to_count=0)
        self.hydras = ZergUnit(UnitTypeId.HYDRALISK, to_count=0)
        self.lurkers = ZergUnit(UnitTypeId.LURKER, to_count=0)
        self.swarmhosts = ZergUnit(UnitTypeId.SWARMHOSTMP, to_count=0)
        self.mutas = ZergUnit(UnitTypeId.MUTALISK, to_count=0)
        self.infestors = ZergUnit(UnitTypeId.INFESTOR, to_count=0)
        self.vipers = ZergUnit(UnitTypeId.VIPER, to_count=0)
        self.corruptors = ZergUnit(UnitTypeId.CORRUPTOR, to_count=0)
        self.broodlords = ZergUnit(UnitTypeId.BROODLORD, to_count=0)
        self.ultras = ZergUnit(UnitTypeId.ULTRALISK, to_count=0)

        self.defense_spines = DefensiveBuilding(
            unit_type=UnitTypeId.SPINECRAWLER, position_type=DefensePosition.Entrance, to_base_index=1, to_count=3
        )

        self.twelve_pool_spines = DefensiveBuilding(
            unit_type=UnitTypeId.SPINECRAWLER, position_type=DefensePosition.Entrance, to_base_index=0, to_count=2
        )

        self.left_spore = DefensiveBuilding(
            unit_type=UnitTypeId.SPORECRAWLER, position_type=DefensePosition.BehindMineralLineLeft
        )
        self.right_spore = DefensiveBuilding(
            unit_type=UnitTypeId.SPORECRAWLER, position_type=DefensePosition.BehindMineralLineRight
        )

        self.triple_middle = DefensiveBuilding(
            unit_type=UnitTypeId.SPORECRAWLER, position_type=DefensePosition.BehindMineralLineCenter, to_count=3
        )

        bc_air_defense = BuildOrder(
            [
                Step(UnitExists(UnitTypeId.SPAWNINGPOOL), self.right_spore, skip_until=self.air_detected,),
                Step(UnitExists(UnitTypeId.SPAWNINGPOOL), self.left_spore, skip_until=self.air_detected,),
                Step(
                    UnitExists(UnitTypeId.SPAWNINGPOOL),
                    self.triple_middle,
                    skip_until=lambda k: k.ai.scout_manager.enemy_build == EnemyBuild.BCRush,
                ),
            ]
        )

        hard_order = SequentialList(
            Step(UnitExists(UnitTypeId.SPAWNINGPOOL), self.twelve_pool_spines, skip_until=self.twelve_pool_detected),
            Step(UnitExists(UnitTypeId.SPAWNINGPOOL), self.defense_spines, skip_until=self.rush_detected,),
            Step(
                UnitExists(UnitTypeId.SPAWNINGPOOL),
                ActBuilding(UnitTypeId.ROACHWARREN, 1),
                skip_until=self.twelve_pool_detected,
            ),
            Step(None, ZergUnit(UnitTypeId.DRONE, to_count=13, only_once=True)),
            Step(None, ZergUnit(UnitTypeId.OVERLORD, to_count=2, only_once=True)),
            Step(None, ZergUnit(UnitTypeId.DRONE, to_count=17, only_once=True)),
            Step(None, ActExpand(2, priority=True, consider_worker_production=False)),
            Step(None, ZergUnit(UnitTypeId.DRONE, to_count=18)),
            Step(RequiredMinerals(120), StepBuildGas(to_count=1)),
            Step(None, ActBuilding(UnitTypeId.SPAWNINGPOOL)),
            Step(None, ZergUnit(UnitTypeId.DRONE, to_count=20)),
            Step(None, ZergUnit(UnitTypeId.QUEEN, to_count=2), skip_until=UnitExists(UnitTypeId.SPAWNINGPOOL)),
            Step(None, ZergUnit(UnitTypeId.ZERGLING, to_count=6), skip_until=UnitExists(UnitTypeId.SPAWNINGPOOL)),
            Step(None, ZergUnit(UnitTypeId.OVERLORD, to_count=3)),
            Step(None, ActExpand(3, priority=True, consider_worker_production=False), skip=self.rush_detected),
        )

        unit_building = BuildOrder(
            [
                Step(None, self.drones, skip_until=self.should_build_drones),
                Step(None, self.queens, skip_until=self.should_build_queens),
                Step(None, self.swarmhosts, skip_until=self.should_build_swarmhosts),
                Step(None, self.lurkers, skip_until=self.should_build_lurkers),
                Step(None, self.hydras, skip_until=self.should_build_hydras),
                Step(None, self.ravagers, skip_until=self.should_build_ravagers),
                Step(None, self.roaches, skip_until=self.should_build_roaches),
                Step(None, self.mutas, skip_until=self.should_build_mutas),
                Step(None, self.infestors, skip_until=self.should_build_infestors),
                Step(None, self.vipers, skip_until=self.should_build_vipers),
                Step(None, self.corruptors, skip_until=self.should_build_corruptors),
                Step(None, self.broodlords, skip_until=self.should_build_broodlords),
                Step(None, self.ultras, skip_until=self.should_build_ultras),
                Step(None, self.banelings, skip_until=self.should_build_banelings),
                Step(None, self.lings, skip_until=self.should_build_lings),
                Step(None, ZergUnit(UnitTypeId.OVERSEER, 3), skip_until=UnitExists(UnitTypeId.LAIR)),
            ]
        )

        tech_buildings = BuildOrder(
            [
                Step(None, ActBuilding(UnitTypeId.SPAWNINGPOOL, to_count=1)),
                Step(UnitExists(UnitTypeId.DRONE, 35), ActBuilding(UnitTypeId.ROACHWARREN)),
                Step(UnitExists(UnitTypeId.ROACHWARREN), ActExpand(3, priority=True, consider_worker_production=False)),
                Step(UnitExists(UnitTypeId.DRONE, 50), MorphLair()),
                Step(UnitExists(UnitTypeId.LAIR), ActBuilding(UnitTypeId.EVOLUTIONCHAMBER, to_count=2)),
                Step(UnitExists(UnitTypeId.LAIR, include_not_ready=True), StepBuildGas(3)),
                Step(
                    UnitExists(UnitTypeId.LAIR),
                    ActBuilding(UnitTypeId.HYDRALISKDEN, to_count=1),
                    # skip_until=self.should_build_hydras,
                ),
                Step(
                    UnitExists(UnitTypeId.HYDRALISKDEN, include_pending=True, include_not_ready=True), StepBuildGas(4)
                ),
                Step(UnitExists(UnitTypeId.HATCHERY, 4), StepBuildGas(6)),
                Step(UnitExists(UnitTypeId.HATCHERY, 5), StepBuildGas(8)),
                Step(
                    RequiredAll(UnitExists(UnitTypeId.LAIR), UnitExists(UnitTypeId.EXTRACTOR, 4)),
                    ActBuilding(UnitTypeId.INFESTATIONPIT),
                    skip_until=self.counter_siege,
                ),
            ]
        )

        upgrades = BuildOrder(
            [
                Step(UnitExists(UnitTypeId.SPAWNINGPOOL), ActTech(UpgradeId.ZERGLINGMOVEMENTSPEED)),
                Step(
                    RequiredAll([UnitExists(UnitTypeId.ROACH), UnitExists(UnitTypeId.LAIR)]),
                    ActTech(UpgradeId.GLIALRECONSTITUTION),
                ),
                SequentialList(
                    Step(
                        RequiredAll(UnitExists(UnitTypeId.HYDRALISKDEN), UnitExists(UnitTypeId.LAIR)),
                        ActTech(UpgradeId.EVOLVEGROOVEDSPINES),
                    ),
                    Step(
                        RequiredAll(
                            UnitExists(UnitTypeId.HYDRALISKDEN),
                            UnitExists(UnitTypeId.LAIR),
                            RequiredTechReady(UpgradeId.EVOLVEGROOVEDSPINES),
                        ),
                        ActTech(UpgradeId.EVOLVEMUSCULARAUGMENTS),
                    ),
                ),
            ]
        )

        scouting = SequentialList(
            Step(RequiredTime(3 * 60), OverlordScout(ScoutLocation.scout_enemy1())),
            Step(RequiredTime(3 * 60), LingScout(1, ScoutLocation.scout_enemy1())),
            Step(RequiredTime(4 * 60), LingScout(2, ScoutLocation.scout_enemy3(), ScoutLocation.scout_enemy2())),
            Step(RequiredTime(6 * 60), OverlordScout(ScoutLocation.scout_enemy1())),
            Step(RequiredTime(7 * 60), LingScout(2, ScoutLocation.scout_enemy4(), ScoutLocation.scout_enemy3())),
        )

        self.distribution = PlanDistributeWorkers(max_gas=3)
        self.roach_response = RoachRushResponse()

        build_steps = BuildOrder(
            bc_air_defense, hard_order, unit_building, StandardUpgrades(), upgrades, tech_buildings
        )
        send_order = BuildOrder(
            Step(None, self.roach_response, skip=lambda k: k.ai.scout_manager.enemy_build != EnemyBuild.RoachRush,),
            Step(None, build_steps, skip=lambda k: k.ai.scout_manager.enemy_build == EnemyBuild.RoachRush,),
            AutoOverLord(),
            self.distribution,
            scouting,
        )

        super().__init__(send_order)

    async def start(self, knowledge: "Knowledge"):
        await super(PaulBuild, self).start(knowledge)
        for order in self.orders:
            await order.start(knowledge)

    def should_take_third(self, knowledge: "Knowledge"):
        if not self.rush_detected():
            return True
        return False

    def air_detected(self, knowledge: "Knowledge"):
        if self.knowledge.enemy_units_manager.enemy_total_power.air_power >= 1:
            return True
        for b in {UnitTypeId.SPIRE, UnitTypeId.STARGATE, UnitTypeId.STARPORT}:
            if b in self.knowledge.known_enemy_structures:
                return True
        if self.ai.scout_manager.enemy_build in {EnemyBuild.BCRush}:
            return True
        return False

    def counter_siege(self, knowledge: "Knowledge"):
        if self.knowledge.known_enemy_units(UnitTypeId.SIEGETANK).amount >= 5:
            return True
        return False

    def twelve_pool_detected(self, knowledge: "Knowledge"):
        if self.ai.time < 3 * 60:
            if self.knowledge.enemy_units_manager.unit_count(UnitTypeId.ZERGLING) >= 4:
                return True
        return False

    def rush_detected(self, knowledge: "Knowledge"):
        if self.knowledge.enemy_race != Race.Zerg:
            if len(self.knowledge.enemy_townhalls) > 1:
                self.enemy_rush = False
                return False
        else:
            if len(self.knowledge.enemy_townhalls) > 2:
                self.enemy_rush = False
                return False

        if self.enemy_rush:
            # we already know they're rushing us
            self.defense_spines.to_base_index = min(
                2, self.get_count(UnitTypeId.HATCHERY, include_not_ready=False, include_pending=False) - 1
            )
            if not self.get_count(
                UnitTypeId.ROACHWARREN, include_not_ready=True, include_pending=True
            ) and not self.get_count(UnitTypeId.HYDRALISKDEN):
                self.distribution.max_gas = 0
            else:
                # full gas if we have a hydra den, 3 if we don't
                self.distribution.max_gas = 21 * self.get_count(UnitTypeId.HYDRALISKDEN) + 3
            return True

        if not self.enemy_nat_scouted:
            enemy_nat = self.knowledge.enemy_expansion_zones[1].center_location
            if self.ai.is_visible(enemy_nat):
                if self.ai.in_pathing_grid(enemy_nat):
                    self.enemy_nat_scouted = True
                    self.enemy_rush = True
                else:
                    self.enemy_nat_scouted = True
        enemy_buildings = self.knowledge.known_enemy_structures
        if enemy_buildings:
            if (
                enemy_buildings.closest_distance_to(self.knowledge.zone_manager.expansion_zones[1].center_location)
                < self.knowledge.rush_distance // 2
            ):
                self.enemy_rush = True
            if len(enemy_buildings(UnitTypeId.ROACHWARREN)) > 0 and self.ai.time <= 4 * 60:
                self.enemy_rush = True
        enemy_power = self.knowledge.enemy_units_manager.enemy_total_power.power
        if enemy_power >= 5 and self.ai.time < 3 * 60:
            self.enemy_rush = True

        if self.enemy_rush:
            self.defense_spines.to_base_index = self.get_count(UnitTypeId.HATCHERY, include_pending=False) - 1

        return self.enemy_rush

    # def roach_rush_detected(self, knowledge):
    #     if self.knowledge.managers.scout_manager.enemy_build == EnemyBuild.RoachRush:
    #         return True
    #     return False

    def should_build_drones(self, knowledge):
        # drone if enemy is BC rushing
        if self.ai.scout_manager.enemy_build != EnemyBuild.BCRush:
            # drone unless we're under attack, saturated, or we can't take their army and they're nearby
            if not self.knowledge.game_analyzer.our_power.is_enough_for(
                self.knowledge.game_analyzer.enemy_predict_power
            ):
                enemy_mobile = self.knowledge.known_enemy_units_mobile
                if enemy_mobile:
                    if (
                        enemy_mobile.closest_distance_to(self.knowledge.zone_manager.expansion_zones[0].center_location)
                        < 50
                    ):
                        return False
            for zone in self.knowledge.zone_manager.expansion_zones:
                if zone.is_ours and zone.is_under_attack:
                    return False
        target_count = min(
            85,
            self.get_count(UnitTypeId.HATCHERY, include_pending=True, include_not_ready=True) * 16
            + self.get_count(UnitTypeId.EXTRACTOR, include_pending=True, include_not_ready=True) * 3,
        )
        if self.cache.own(UnitTypeId.DRONE).amount < target_count:
            self.drones.to_count = target_count
            return True
        else:
            return False

    def should_build_lings(self, knowledge):
        if self.get_count(UnitTypeId.SPAWNINGPOOL):
            self.lings.to_count = 100
            return True
        return False

    def should_build_queens(self, knowledge):
        """Hatcheries + 3 queens, max 6"""
        if self.get_count(UnitTypeId.SPAWNINGPOOL):
            if self.ai.scout_manager.enemy_build == EnemyBuild.BCRush:
                self.queens.to_count = 12
                return True
            target_count = min(6, self.get_count(UnitTypeId.HATCHERY) + 3)
            if self.cache.own(UnitTypeId.QUEEN).amount < target_count:
                self.queens.to_count = target_count
                return True
        return False

    def should_build_roaches(self, knowledge):
        if self.get_count(UnitTypeId.ROACHWARREN):
            if not self.get_count(UnitTypeId.LAIR):
                self.roaches.to_count = 100
            elif self.knowledge.game_analyzer.enemy_power.air_presence < 10:
                self.roaches.to_count = 40
            else:
                if self.get_count(UnitTypeId.HYDRALISKDEN, include_pending=False, include_not_ready=False):
                    self.roaches.to_count = 0
                    return False
                else:
                    self.roaches.to_count = 20
            return True
        return False

    def should_build_ravagers(self, knowledge):
        roach_num = self.cache.own(UnitTypeId.ROACH).amount
        if roach_num:
            self.ravagers.to_count = roach_num // 3
            return True
        return False

    def should_build_hydras(self, knowledge):
        if self.get_count(UnitTypeId.HYDRALISKDEN):
            if not self.counter_siege:
                self.hydras.to_count = 40
                return True
            else:
                if self.air_detected(knowledge):
                    self.hydras.to_count = 15
                    return True
                self.hydras.to_count = 0
        return False

    def should_build_swarmhosts(self, knowledge):
        if self.get_count(UnitTypeId.INFESTATIONPIT):
            if self.counter_siege:
                self.swarmhosts.to_count = 16
                return True
        return False

    def should_build_banelings(self, knowledge):
        if self.get_count(UnitTypeId.BANELINGNEST):
            self.banelings.to_count = self.cache.own(UnitTypeId.ZERGLING).amount
            return True
        return False

    def should_build_lurkers(self, knowledge):
        # lurker den is broken
        return False
        # if self.get_count(UnitTypeId.LURKERDEN):
        #     self.lurkers.to_count = self.cache.own(UnitTypeId.HYDRALISK).amount // 2
        #     return True
        # return False

    def should_build_mutas(self, knowledge):
        if self.get_count(UnitTypeId.SPIRE):
            self.mutas.to_count = 20
            return True
        return False

    def should_build_infestors(self, knowledge):
        """Doesn't set count above 0 because we're not building them"""
        if self.get_count(UnitTypeId.INFESTATIONPIT):
            return True
        return False

    def should_build_vipers(self, knowledge):
        """Doesn't set count above 0 because we're not building them"""
        if self.get_count(UnitTypeId.INFESTATIONPIT):
            return True
        return False

    def should_build_corruptors(self, knowledge):
        """Doesn't set count above 0 because we're not building them"""
        if self.get_count(UnitTypeId.SPIRE):
            return True
        return False

    def should_build_broodlords(self, knowledge):
        """Doesn't set count above 0 because we're not building them"""
        if self.get_count(UnitTypeId.GREATERSPIRE):
            return True
        return False

    def should_build_ultras(self, knowledge):
        if self.get_count(UnitTypeId.ULTRALISKCAVERN):
            self.ultras.to_count = 10
            return True
        return False
