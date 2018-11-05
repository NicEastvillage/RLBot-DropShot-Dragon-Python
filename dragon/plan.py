from RLUtilities.Maneuvers import *
from RLUtilities.LinearAlgebra import *

from dropshot import DropshotBall


class Plan:
    def __init__(self, steps):
        self.steps = steps
        self.step_count = len(steps)
        self.current = 0
        self.finished = False

    def execute(self, bot):

        step_finished = self.steps[self.current].execute(bot)
        if step_finished:
            if self.current < self.step_count - 1:
                self.current += 1
            else:
                self.finished = True

        return self.finished


class KickoffPlan:

    DRIVE = 0
    AERIAL = 1

    def __init__(self):
        self.state = KickoffPlan.DRIVE
        self.action = None
        self.finished = False

    def execute(self, bot):

        if self.action == None:
            self.action = Drive(bot.info.my_car, vec3(0, 0, 0), 2400)

        self.action.step(0.016666)
        dist = norm(bot.info.my_car.pos)

        if dist < 2600 and self.state == KickoffPlan.DRIVE:
            self.state = KickoffPlan.AERIAL
            # Aerial with empty values
            self.action = Aerial(bot.info.my_car, vec3(0, 0, 0), 0)
            # predict where ball can be hit
            ball = DropshotBall(bot.info.ball)

            for i in range(60):
                ball.step(0.016666)

                self.action.target = ball.pos
                self.action.t_arrival = ball.t

                # check if we can reach it by an aerial
                if self.action.is_viable():
                    self.action.target += vec3(0, 0, 15)
                    break

        if self.state == KickoffPlan.DRIVE:
            bot.renderer.draw_string_3d(bot.info.my_car.pos, 1, 1, "Drive", bot.renderer.white())
        else:
            bot.renderer.draw_string_3d(bot.info.my_car.pos, 1, 1, "Arial", bot.renderer.white())

        bot.controls = self.action.controls
        self.finished = not bot.info.is_kickoff
        return self.finished


class DodgeTowardsPlan:
    def __init__(self, target, jump_duration=0.1):
        self.target = target
        self.jump_duration = jump_duration
        self.dodge = None
        self.finished = False

    def execute(self, bot):
        if self.dodge == None:
            self.dodge = AirDodge(bot.info.my_car, self.jump_duration, self.target)

        self.dodge.step(0.016666)
        bot.controls = self.dodge.controls
        self.finished = self.dodge.finished
        return self.dodge.finished
