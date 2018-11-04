from RLUtilities.LinearAlgebra import *

from dropshot import *
from tiles import Tile


class DropshotAnalyzer:

    TILE_FOCUS_WEIGHTS = {
        Tile.UNKNOWN: 0,
        Tile.FILLED: 0.1,
        Tile.DAMAGED: 0.4,
        Tile.OPEN: 1.0
    }

    def __init__(self):
        self.best_target_dir = vec3(0, 0, 0)
        self.best_target_tile = None

    def read_info(self, info: DropshotInfo):
        car_to_ball = info.ball.pos - info.my_car.pos
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

