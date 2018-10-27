import math
import random

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from RLUtilities.Maneuvers import *
from RLUtilities.GameInfo import *
from RLUtilities.Simulation import *
from RLUtilities.LinearAlgebra import *

class Dragon(BaseAgent):

    def __init__(self, name, team, index):
        self.info = GameInfo(index, team)
        self.controls = SimpleControllerState()
        self.kickoff = False
        self.action = None
        self.ball_predictions = []

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        self.info.read_packet(packet)

        if self.action == None or self.action.finished:
            self.action = Drive(self.info.my_car, self.info.ball.pos, 2300)
        else:
            self.action.target_pos = self.info.ball.pos
        self.action.step(0.01666)
        return self.action.controls
