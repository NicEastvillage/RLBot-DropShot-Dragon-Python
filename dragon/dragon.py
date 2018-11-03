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
from usystem import UtilitySystem, AtbaChoice


class Dragon(BaseAgent):

    def __init__(self, name, team, index):
        self.name = name
        self.team = team
        self.index = index
        self.info = DropshotInfo(index, team)
        self.controls = SimpleControllerState()
        self.plan = None
        self.action = None
        self.ut = UtilitySystem([AtbaChoice()])

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        self.info.read_packet(packet)
        self.renderer.begin_rendering()

        if self.plan == None or self.plan.finished:
            self.plan = None
            choice, score = self.ut.evaluate(self)
            choice.execute(self)
            if self.plan != None:
                self.ut.reset()
        else:
            self.plan.execute(self)

        if self.team == 0:
            draw_ball_trajectory(self)

        self.info.my_car.last_input.roll = self.controls.roll
        self.info.my_car.last_input.pitch = self.controls.pitch
        self.info.my_car.last_input.yaw = self.controls.yaw

        self.renderer.end_rendering()
        return self.action.controls


def draw_ball_trajectory(bot):
    prediction = DropshotBall(bot.info.ball)
    ball_predictions = [vec3(prediction.pos)]
    for i in range(150):
        prediction.step_ds(1. / 30)
        ball_predictions.append(vec3(prediction.pos))
    bot.renderer.draw_polyline_3d(ball_predictions, bot.renderer.red())


def draw_tiles(bot):
    blue = bot.renderer.create_color(255, 80, 170, 255)
    orange = bot.renderer.create_color(255, 255, 170, 30)
    red = bot.renderer.create_color(255, 255, 30, 80)

    for tile in bot.info.tile_list:
        if tile.team == 1:
            color = blue if tile.team == 0 else orange
            if tile.state == tile.OPEN:
                color = red
                bot.renderer.draw_rect_3d(tile.location, 10, 10, tile.state == tile.FILLED, color)


def draw_all_positions(bot):
    blue = bot.renderer.create_color(255, 80, 170, 255)
    orange = bot.renderer.create_color(255, 255, 170, 30)
    for car in bot.info.cars:
        color = blue if car.team == 0 else orange
        renderhelp.highlight_point_on_tile(bot.renderer, bot.info, car.pos, color)
    red = bot.renderer.create_color(255, 255, 30, 80)
    renderhelp.highlight_point_on_tile(bot.renderer, bot.info, bot.info.ball.pos, red)
