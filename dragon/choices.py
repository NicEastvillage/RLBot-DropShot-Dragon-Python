import math

from RLUtilities.LinearAlgebra import *
from RLUtilities.Maneuvers import Drive

import tiles
import rlmath
from dropshot import DropshotBall
from plan import DodgeTowardsPlan


class DefensiveWait:
    def __init__(self, bot):
        pass

    def utility(self, bot):
        # The more the ball is on the enemy side in 3 seconds the more likely it is to DefWait
        ball_3_sec_pos = DropshotBall(bot.info.ball).step_ds(3.0).pos
        ball_side_01 = 1 / (1 + 2 ** (bot.tsgn * ball_3_sec_pos[1] / 400))
        return rlmath.clamp01(0.7 * ball_side_01)

    def execute(self, bot):
        bot.renderer.draw_string_3d(bot.info.my_car.pos, 1, 1, "DefWait", bot.renderer.yellow())

        ball_pos = bot.info.ball.pos
        target = vec3(ball_pos[0], -ball_pos[1], 0)
        distance = norm(target - bot.info.my_car.pos)
        speed = distance / 3

        bot.renderer.draw_line_3d(bot.info.my_car.pos, target, bot.renderer.yellow())

        drive = Drive(bot.info.my_car, target, speed)
        drive.step(0.016666)
        bot.controls = drive.controls


class Dribble:
    def __init__(self, bot):
        self.is_dribbling = False
        self.extra_bias = 0.2
        self.wait_before_flick = 0.18
        self.flick_timer = 0
        pass

    def utility(self, bot):
        car_to_ball = bot.info.my_car.pos - bot.info.ball.pos

        dist_01 = rlmath.clamp01(1 - norm(car_to_ball) / 3000)

        head_dir = rlmath.lerp(vec3(0, 0, 1), bot.info.my_car.forward(), 0.1)
        ang = angle_between(head_dir, car_to_ball)
        ang_01 = rlmath.clamp01(1 - ang / (math.pi / 2))
        on_my_side_b = (sgn(bot.info.ball.pos[1]) == bot.tsgn)

        ball_landing_pos = bot.info.ball.next_landing().data
        tile = tiles.point_to_tile(bot.info, ball_landing_pos)
        protect_tile_b = (tile != None and tile.team == bot.team and
                          (tile.state == tiles.Tile.OPEN or bot.info.ball.team != bot.team))

        return rlmath.clamp01(0.1 + 0.3 * on_my_side_b + 0.3 * ang_01 + 0.3 * dist_01 + 0.8 * protect_tile_b + self.is_dribbling * self.extra_bias)

    def execute(self, bot):
        bot.renderer.draw_string_3d(bot.info.my_car.pos, 1, 1, "Dribble", bot.renderer.purple())
        self.is_dribbling = True

        BIAS = 35
        ball_landing = bot.info.ball.next_landing()
        tile = tiles.point_to_tile(bot.info, ball_landing.data)

        if tile != None and tile.team != bot.team and tile.state == tiles.Tile.OPEN:
            # It will hit enemy open tile - so don't save
            target = ball_landing.data
            speed = norm(target - bot.info.my_car.pos) / 2.0
        else:
            target = ball_landing.data - BIAS * bot.analyzer.best_target_dir
            dist = norm(target - bot.info.my_car.pos)
            speed = 1400 if ball_landing.time == 0 else dist / ball_landing.time

        car_to_ball = bot.info.ball.pos - bot.info.my_car.pos
        dist = norm(car_to_ball)
        print(bot.team, ":", dist, ":", self.flick_timer)
        if dist <= 185:
            self.flick_timer += 0.016666
            if self.flick_timer > self.wait_before_flick:
                bot.plan = DodgeTowardsPlan(bot.analyzer.best_target_tile.location, 0.07)
        else:
            self.flick_timer = 0

        drive = Drive(bot.info.my_car, target, speed)
        drive.step(0.016666)
        bot.controls = drive.controls

    def reset(self):
        self.is_dribbling = False
        self.flick_timer = 0
