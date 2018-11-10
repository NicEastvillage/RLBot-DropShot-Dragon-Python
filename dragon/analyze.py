from RLUtilities.LinearAlgebra import *

import rlmath
from dropshot import *
from tiles import Tile


class DropshotAnalyzer:

    TILE_FOCUS_WEIGHTS = {
        Tile.UNKNOWN: 0,
        Tile.FILLED: 0.3,
        Tile.DAMAGED: 0.6,
        Tile.OPEN: 1.0
    }

    def __init__(self):
        self.best_target_dir = vec3(0, 0, 0)
        self.best_target_tile = None
        self.team_mate_has_ball_01 = 0
        self.team_mate_is_defensive_01 = 0
        self.nearest_team_mate = None

    def read_info(self, info: DropshotInfo):
        ball_pos = info.ball.pos
        # Find target tile
        car_to_ball = ball_pos - info.my_car.pos
        best_score = -1
        best_dir = None
        offset = 70 * (1 - info.my_car.team)
        for tile in info.tile_list[offset:70 + offset]:
            ball_to_tile = tile.location - info.ball.pos
            ang = angle_between(car_to_ball, ball_to_tile)
            score = (1 - ang / math.pi) * DropshotAnalyzer.TILE_FOCUS_WEIGHTS[tile.state]
            if score > best_score:
                best_score = score
                best_dir = ball_to_tile
                self.best_target_tile = tile
        self.best_target_dir = normalize(best_dir)

        # Analyze team mates
        def_pos = vec3(ball_pos[0], -ball_pos[1], 0)
        dist_ball = norm(car_to_ball)
        tm_closer_ball = False
        tm_closest_ball_dist = 99999
        tm_closest_def_dist = 99999
        tm_nearest_mate = None
        tm_nearest_mate_dist = 99999
        for car in info.teammates:
            tm_dist_ball = norm(info.ball.pos - car.pos)
            if tm_dist_ball < dist_ball and tm_dist_ball < tm_closest_ball_dist:
                tm_closer_ball = True
                tm_closest_ball_dist = tm_dist_ball
            tm_dist_def = norm(def_pos - car.pos)
            if tm_dist_def < tm_closest_def_dist:
                tm_closest_def_dist = tm_dist_def
            tm_dist_me = norm(car.pos - info.my_car.pos)
            if tm_nearest_mate == None or tm_dist_me < tm_nearest_mate_dist:
                tm_nearest_mate = car
                tm_nearest_mate_dist = tm_dist_me

        self.team_mate_has_ball_01 = (1 - rlmath.clamp01(tm_closest_ball_dist / 1000)) ** 2 if tm_closer_ball else 0
        self.team_mate_is_defensive_01 = (1 - rlmath.clamp01(tm_closest_ball_dist / 4000))
