from RLUtilities.LinearAlgebra import *
from RLUtilities.Maneuvers import Drive

from dropshot import DropshotBall


def clamp01(v):
    if v < 0:
        return 0
    if v > 1:
        return 1
    return v


class DefensiveWait:
    def __init__(self, bot):
        pass

    def utility(self, bot):
        # The more the ball is on the enemy side in 3 seconds the more likely it is to DefWait
        ball_3_sec_pos = DropshotBall(bot.info.ball).step_ds(3.0).pos
        ball_side_01 = 1 / (1 + 2 ** (bot.tsgn * ball_3_sec_pos[1] / 400))
        return clamp01(ball_side_01)

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
