import math
import random

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from RLUtilities.Maneuvers import *
from RLUtilities.GameInfo import *
from RLUtilities.Simulation import *
from RLUtilities.LinearAlgebra import *

from dropshot import DropshotInfo


class Dragon(BaseAgent):

    def __init__(self, name, team, index):
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