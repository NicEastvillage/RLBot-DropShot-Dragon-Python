import math
import random

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from RLUtilities.Maneuvers import *
from RLUtilities.GameInfo import *
from RLUtilities.Simulation import *
from RLUtilities.LinearAlgebra import *

import renderhelp
from dropshot import *


class Dragon(BaseAgent):

    def __init__(self, name, team, index):
        self.name = name
        self.team = team
        self.index = index
        self.info = DropshotInfo(index, team)
        self.controls = SimpleControllerState()
        self.action = None

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        self.info.read_packet(packet)

        if self.action == None or self.action.finished:
            self.action = Drive(self.info.my_car, self.info.ball.pos, 2300)
        else:
            self.action.target_pos = self.info.ball.pos
        self.action.step(0.01666)

        if self.team == 0:
            prediction = DropshotBall(self.info.ball)
            ball_predictions = [vec3(prediction.pos)]
            
            for i in range(150):
                prediction.step_ds(1./15)
                ball_predictions.append(vec3(prediction.pos))

            self.renderer.begin_rendering()
            self.renderer.draw_polyline_3d(ball_predictions, self.renderer.red())
            self.renderer.end_rendering()

        return self.action.controls


def draw_tiles(renderer, info):
    blue = renderer.create_color(255, 80, 170, 255)
    orange = renderer.create_color(255, 255, 170, 30)
    red = renderer.create_color(255, 255, 30, 80)

    for tile in info.tile_list:
        if tile.team == 1:
            color = blue if tile.team == 0 else orange
            if tile.state == tile.OPEN:
                color = red
            renderer.draw_rect_3d(tile.location, 10, 10, tile.state == tile.FILLED, color)


def draw_all_positions(renderer, info):
    blue = renderer.create_color(255, 80, 170, 255)
    orange = renderer.create_color(255, 255, 170, 30)
    for car in info.cars:
        color = blue if car.team == 0 else orange
        renderhelp.highlight_point_on_tile(renderer, info, car.pos, color)
    red = renderer.create_color(255, 255, 30, 80)
    renderhelp.highlight_point_on_tile(renderer, info, info.ball.pos, red)
