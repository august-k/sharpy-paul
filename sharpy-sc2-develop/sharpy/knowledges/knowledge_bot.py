import logging
import sys
import threading
from abc import abstractmethod

from sc2.units import Units
from sharpy.knowledges import Knowledge
from sharpy.plans import BuildOrder
from config import get_config, get_version
from sc2 import BotAI, Result, Optional, UnitTypeId, position
from sc2.unit import Unit
from sc2.position import Point2
import time
import json
import numpy as np
from sklearn.cluster import KMeans

OVERLORD_PATH = "sharpy/knowledges/"


class KnowledgeBot(BotAI):
    """Base class for bots that are built around Knowledge class."""

    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self.config = get_config()
        self.knowledge: Knowledge = None
        self.plan: BuildOrder = None
        self.knowledge = Knowledge()
        self.start_plan = True
        self.run_custom = False
        self.realtime_worker = True
        self.realtime_split = True
        self.last_game_loop = -1
        self.distance_calculation_method = 0
        self.unit_command_uses_self_do = True
        self.hidden_ol_spots: List[Point2] = None
        self.ol_spot_index: int = 0

    async def real_init(self):
        self.knowledge.pre_start(self)
        await self.knowledge.start()
        self.plan = await self.create_plan()
        if self.start_plan:
            await self.plan.start(self.knowledge)

        self._log_start()

    async def chat_init(self):
        if self.knowledge.is_chat_allowed:
            msg = self._create_start_msg()
            await self.chat_send(msg)

    def _create_start_msg(self) -> str:
        msg: str = ""

        if self.name is not None:
            msg += self.name

        version = get_version()
        if len(version) >= 2:
            msg += f" {version[0]} {version[1]}"

        return msg

    async def chat_send(self, message: str):
        # todo: refactor to use chat manager?
        self.knowledge.print(message, "Chat")
        await super().chat_send(message)

    @abstractmethod
    async def create_plan(self) -> BuildOrder:
        pass

    async def on_before_start(self):
        """
        Override this in your bot class. This function is called before "on_start"
        and before expansion locations are calculated.
        Not all data is available yet.
        """

        # Start building first worker before doing any heavy calculations
        # This is only needed for real time, but we don't really know whether the game is real time or not.
        # await self.start_first_worker()
        self._client.game_step = int(self.config["general"]["game_step_size"])

        if self.realtime_split:
            # Split workers
            mfs = self.mineral_field.closer_than(10, self.townhalls.first.position)
            workers = Units(self.workers, self)

            for mf in mfs:  # type: Unit
                if workers:
                    worker = workers.closest_to(mf)
                    self.do(worker.gather(mf))
                    workers.remove(worker)

            for w in workers:  # type: Unit
                self.do(w.gather(mfs.closest_to(w)))
            await self._do_actions(self.actions)
            self.actions.clear()

    async def on_start(self):
        """Allows initializing the bot when the game data is available."""
        await self.real_init()
        with open(f"{OVERLORD_PATH}cached_overlord_spots.json", "r") as f:
            overlord_spots = json.load(f)
        map_name = self.game_info.map_name
        if map_name not in overlord_spots:
            self.calculate_overlord_spots()
            overlord_spots[map_name] = [tuple(pos) for pos in self.hidden_ol_spots]
            with open(f"{OVERLORD_PATH}cached_overlord_spots.json", "w") as f:
                json.dump(overlord_spots, f, indent="\t")
        else:
            self.hidden_ol_spots = [Point2(pos) for pos in overlord_spots[map_name]]

    async def on_step(self, iteration):
        try:
            if iteration == 10:
                await self.chat_init()

            if not self.realtime and self.last_game_loop == self.state.game_loop:
                self.realtime = True
                self.client.game_step = 1
                return

            self.last_game_loop = self.state.game_loop

            ns_step = time.perf_counter_ns()
            await self.knowledge.update(iteration)
            await self.pre_step_execute()
            await self.plan.execute()

            await self.knowledge.post_update()

            if self.knowledge.debug:
                await self.plan.debug_draw()

            ns_step = time.perf_counter_ns() - ns_step
            ms_step = ns_step / 1000 / 1000

            if ms_step > 100:
                self.knowledge.print(
                    f"Step {self.state.game_loop} took {round(ms_step)} ms.",
                    "LAG",
                    stats=False,
                    log_level=logging.WARNING,
                )

        except:  # noqa, catch all exceptions
            e = sys.exc_info()[0]
            logging.exception(e)

            # do we want to raise the exception and crash? or try to go on? :/
            raise

    async def pre_step_execute(self):
        pass

    async def on_unit_destroyed(self, unit_tag: int):
        if self.knowledge.ai is not None:
            await self.knowledge.on_unit_destroyed(unit_tag)

    async def on_unit_created(self, unit: Unit):
        if self.knowledge.ai is not None:
            await self.knowledge.on_unit_created(unit)
        if unit.type_id == UnitTypeId.OVERLORD:
            if self.ol_spot_index + 1 >= len(self.hidden_ol_spots):
                return
            else:
                self.do(unit.move(Point2(self.hidden_ol_spots[self.ol_spot_index])))
                self.ol_spot_index += 1

    async def on_building_construction_started(self, unit: Unit):
        if self.knowledge.ai is not None:
            await self.knowledge.on_building_construction_started(unit)

    async def on_building_construction_complete(self, unit: Unit):
        if self.knowledge.ai is not None:
            await self.knowledge.on_building_construction_complete(unit)

    async def on_end(self, game_result: Result):
        if self.knowledge.ai is not None:
            await self.knowledge.on_end(game_result)

    def _log_start(self):
        def log(message):
            self.knowledge.print(message, tag="Start", stats=False)

        log(f"My race: {self.knowledge.my_race.name}")
        log(f"Opponent race: {self.knowledge.enemy_race.name}")
        log(f"OpponentId: {self.opponent_id}")

    # async def start_first_worker(self):
    #     if self.townhalls and self.realtime_worker:
    #         townhall = self.townhalls.first
    #         if townhall.type_id == UnitTypeId.COMMANDCENTER:
    #             await self.synchronous_do(townhall.train(UnitTypeId.SCV))
    #         if townhall.type_id == UnitTypeId.NEXUS:
    #             await self.synchronous_do(townhall.train(UnitTypeId.PROBE))
    #         if townhall.type_id == UnitTypeId.HATCHERY:
    #             await self.synchronous_do(townhall.train(UnitTypeId.DRONE))

    def calculate_overlord_spots(self):
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
        """ Calculates an index value score on a model and its predicted clusters

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

        sl = np.array([start[0], start[1]])
        sl = np.expand_dims(sl, 0)
        # euclidean distance on multiple points to a single point
        dist = (points - sl) ** 2
        dist = np.sum(dist, axis=1)
        dist = np.sqrt(dist)
        return dist
