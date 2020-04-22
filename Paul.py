"""Main code for running Paul."""
from typing import List, Optional, Dict

import numpy as np
import sc2
from sc2 import position
from sc2.data import AIBuild, Difficulty, Race
from sc2.ids.unit_typeid import UnitTypeId
from sc2.player import Bot, Computer
from sc2.position import Point2
from sc2.unit import Unit
from sklearn.cluster import KMeans

from paul_plans.build_manager import BuildSelector
from paul_plans.opening import ViBE
from sharpy.knowledges import KnowledgeBot
from sharpy.managers import ManagerBase
from sharpy.managers.unit_role_manager import UnitTask
from sharpy.plans import BuildOrder, Step
from sharpy.plans.tactics import (
    PlanDistributeWorkers,
    PlanFinishEnemy,
    PlanWorkerOnlyDefense,
    PlanZoneAttack,
    PlanZoneDefense,
    PlanZoneGather,
)
from sharpy.plans.tactics.zerg import InjectLarva, SpreadCreep
from sharpy.plans.require import RequireCustom
from paul_plans.opening.ling_rush import LingRush
from paul_plans.roach_ravager_swarmhost import RRSH

allowed_builds = {
    "ViBE": ViBE(),
    "ling_flood": LingRush(),
    "roach_ravager_swarmhost": RRSH(),
    # TODO: add enemy_one_base defense plan
}


class PostOpening(BuildOrder):
    """Pull predefined build orders based on scouting information."""

    pass


class PaulBot(KnowledgeBot):
    """Run Paul."""

    def __init__(self, build_name: str = ""):
        """Set up attack parameters and name."""
        super().__init__("Paul")
        self.my_race = Race.Zerg
        self.attack = PlanZoneAttack(120)
        self.attack.retreat_multiplier = 0.3
        self.build_name = build_name
        self.build_selector = BuildSelector(build_name)
        self.hidden_ol_spots: List[Point2]
        self.hidden_ol_index: int = 0
        self.scout_ling_count = 0
        self.ling_scout_location: Dict[int, Point2]

    async def create_plan(self) -> BuildOrder:
        """Turn plan into BuildOrder."""
        attack_tactics = [
            PlanZoneGather(),
            PlanZoneDefense(),
            self.attack,
            PlanFinishEnemy(),
            PlanWorkerOnlyDefense(),
        ]

        # builds = []
        # for key, build_order_call in allowed_builds:
        #     builds.append(
        #         Step(None, build_order_call(), skip_until=lambda k, key=key: self.build_selector.response == key)
        #     )
        builds = [
            Step(None, ViBE(), skip_until=RequireCustom(lambda k: k.ai.build_selector.response == "ViBE")),
            Step(
                None,
                RRSH(),
                skip_until=RequireCustom(lambda k: k.ai.build_selector.response == "roach_ravager_swarmhost"),
            ),
        ]
        return BuildOrder([builds, attack_tactics, PlanDistributeWorkers(), InjectLarva(), SpreadCreep()])

    async def on_start(self):
        """
        Calculate and sort Overlord hidden spots.

        Automatically called at the start of the game once game info is available.
        """
        await self.real_init()
        self.calculate_overlord_spots()
        self.hidden_ol_spots.sort(
            key=lambda x: self.knowledge.ai._distance_pos_to_pos(x, self.knowledge.enemy_main_zone.center_location),
        )
        self.ling_scout_location = {
            0: self.knowledge.zone_manager.enemy_expansion_zones[1].gather_point,
            1: self.knowledge.zone_manager.enemy_expansion_zones[2].gather_point,
            2: self.knowledge.ai.game_info.map_center,
            3: self.knowledge.zone_manager.expansion_zones[2].gather_point,
        }

    def configure_managers(self) -> Optional[List[ManagerBase]]:
        """Add custom managers."""
        return [self.build_selector]

    async def on_unit_created(self, unit: Unit):
        """Send Overlords and lings to scouting spots."""
        if unit.type_id == UnitTypeId.OVERLORD:
            if self.hidden_ol_index + 1 >= len(self.hidden_ol_spots):
                return
            else:
                if self.hidden_ol_index == 0:
                    self.do(
                        unit.move(
                            self.knowledge.zone_manager.enemy_expansion_zones[0].center_location.towards(
                                self.knowledge.ai.game_info.map_center, 11
                            )
                        )
                    )
                self.do(unit.move(self.hidden_ol_spots[self.hidden_ol_index], queue=True))
                self.hidden_ol_index += 1

        elif unit.type_id == UnitTypeId.ZERGLING:
            if self.scout_ling_count in self.ling_scout_location:
                self.do(unit.move(self.ling_scout_location[self.scout_ling_count]))
                self.knowledge.roles.set_task(UnitTask.Scouting, unit)
                self.scout_ling_count += 1

    def calculate_overlord_spots(self):
        """Calculate hidden overlord spots for scouting."""
        # first get all highground tiles
        max_height: int = np.max(self.game_info.terrain_height.data_numpy)
        highground_spaces: np.array = np.where(self.game_info.terrain_height.data_numpy == max_height)

        # stack the y and x coordinates together, transpose the matrix for
        # easier use, this then reflects x and y coordinates
        all_highground_tiles: np.array = np.vstack((highground_spaces[1], highground_spaces[0])).transpose()

        # get distances of high ground tiles to start
        dist_from_start: np.array = self.calculate_distance_points_from_location(
            self.start_location, all_highground_tiles
        )
        # get ids of all tiles that are further than 30
        valid_tiles_start: np.array = np.where(dist_from_start > 30)[0]

        # get all distances of high ground tiles to enemy start
        dist_from_enemy_start: np.array = self.calculate_distance_points_from_location(
            self.enemy_start_locations[0], all_highground_tiles
        )

        # get ids of all tiles that are further than 30
        valid_tiles_enemy_start: np.array = np.where(dist_from_enemy_start > 30)[0]

        # valid tiles = where valid_tiles_start == valid_tiles_enemy_start
        valid_tiles_idx: np.array = np.intersect1d(valid_tiles_start, valid_tiles_enemy_start)

        # finally, store all coordinates that are valid
        valid_tiles: np.array = all_highground_tiles[valid_tiles_idx]

        self.hidden_ol_spots = self.find_highground_centroids(valid_tiles)

    def find_highground_centroids(self, highground_tiles) -> np.array:
        """Find the centroids of the highground clusters for KMeans."""
        # using db index, find the optimal number of clusters for kmeans
        range_of_k = range(4, 22)
        # store all the davies-bouldin index values
        dbindexes = []

        for k in range_of_k:
            # try kmeans for each k value
            kmeans = KMeans(n_clusters=k, random_state=42).fit(highground_tiles)
            dbindexes.append(self.davis_bouldin_index(highground_tiles, kmeans.labels_, k))

        kmeans = KMeans(n_clusters=np.argmin(dbindexes) + 4, random_state=42).fit(highground_tiles)

        ol_spots: List[Point2] = [Point2(position.Pointlike((pos[0], pos[1]))) for pos in kmeans.cluster_centers_]

        # each clusters centroid is the overlord positions
        return ol_spots

    def davis_bouldin_index(self, X, y_pred, k):
        """
        Calculate an index value score on a model and its predicted clusters.

        Parameters
        ----------
        X : np matrix
            the whole dataset
        y_pred : np array
            array of indices indicating which values of X belong to a cluster
        k : int
            number of clusters

        Returns
        -------
        float
            Davies_Bouldin index
        """

        def euclidean_distance(x, y):
            return np.sqrt(np.sum(np.square(x - y)))

        # somewhere to store distances in each cluster
        distances = [[] for i in range(k)]
        # somewhere to store the centroids for each cluster
        centroids = np.zeros(k * 2).reshape(k, 2)

        # compute euclidean distance between each point
        # to its clusters centroid
        for i in range(k):
            centroids[i] = np.array([np.mean(X[y_pred == i, :1]), np.mean(X[y_pred == i, 1:])])
            for sample in X[y_pred == i]:
                distances[i].append(euclidean_distance(sample, centroids[i]))

        # now all the distances have been computed,
        # calculate the mean distances for each cluster
        mean_distances = [np.mean(distance) for distance in distances]

        # will hold the summation of max value for the ratio
        # within-to-between clusters i and j
        dbi = 0
        for i in range(k):
            max_distance = 0.0
            for j in range(k):
                if i != j:
                    # ratio within-to-between clusters i and j
                    values = (mean_distances[i] + mean_distances[j]) / euclidean_distance(centroids[i], centroids[j])
                    # if worst case so far change max_distance to the value
                    if values > max_distance:
                        max_distance = values
            # add worst case distance for this pair of clusters to dbi
            dbi += max_distance

        # returns the average of all the worst cases
        # between each pair of clusters
        return dbi / k

    def calculate_distance_points_from_location(self, start: Point2, points: np.array) -> np.array:
        """Determine distance from point to start location."""
        sl = np.array([start[0], start[1]])
        sl = np.expand_dims(sl, 0)
        # euclidean distance on multiple points to a single point
        dist = (points - sl) ** 2
        dist = np.sum(dist, axis=1)
        dist = np.sqrt(dist)
        return dist


def main():
    """Run things."""
    sc2.run_game(
        sc2.maps.get("TritonLE"),
        [Bot(Race.Zerg, PaulBot()), Computer(Race.Terran, Difficulty.VeryHard, AIBuild.Rush)],
        realtime=False,
        save_replay_as="Paul2.SC2Replay",
    )


if __name__ == "__main__":
    main()
