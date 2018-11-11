import math

from RLUtilities.LinearAlgebra import *
from RLUtilities.Maneuvers import Drive, Aerial, AerialTurn
from rlbot.agents.base_agent import SimpleControllerState

import tiles
import rlmath
from dropshot import DropshotBall
from plan import DodgeTowardsPlan, AerialPlan


class DefensiveWait:
    def __init__(self, bot):
        self.drive = Drive(None, None, 0)
        pass

    def utility(self, bot):
        # The more the ball is on the enemy side in 3 seconds the more likely it is to DefWait
        ball_3_sec_pos = DropshotBall(bot.info.ball).step_ds(3.0).pos
        ball_side_01 = 1 / (1 + 2 ** (bot.tsgn * ball_3_sec_pos[1] / 400))
        return rlmath.clamp01(0.7 * ball_side_01 - 0.55 * bot.analyzer.team_mate_is_defensive_01)

    def execute(self, bot):
        bot.renderer.draw_string_3d(bot.info.my_car.pos, 1, 1, "DefWait", bot.renderer.yellow())

        ball_pos = bot.info.ball.pos
        target = vec3(ball_pos[0], -ball_pos[1], 0)
        target = rlmath.lerp(target, vec3(0, 0, 0), bot.analyzer.team_mate_is_defensive_01)

        for car in bot.info.teammates:
            to_me_n = normalize(bot.info.my_car.pos - car.pos)
            target += to_me_n * 400

        bot.renderer.draw_line_3d(bot.info.my_car.pos, target, bot.renderer.yellow())

        distance = norm(target - bot.info.my_car.pos)
        if distance > 2000:
            ctt_n = normalize(target - bot.info.my_car.pos)
            vtt = dot(bot.info.my_car.vel, ctt_n) / dot(ctt_n, ctt_n)
            if vtt > 750:
                bot.plan = DodgeTowardsPlan(target)

        speed = min(1410, distance / 3)
        self.drive.car = bot.info.my_car
        self.drive.target_pos = target
        self.drive.target_speed = speed
        self.drive.step(0.016666)
        bot.controls = self.drive.controls


class AirDrag:
    def __init__(self, bot):
        self.is_dribbling = False
        self.flick_timer = 0

        # Constants
        self.drive = Drive(None, None, 0)
        self.extra_utility_bias = 0.2
        self.wait_before_flick = 0.18
        self.flick_init_jump_duration = 0.07
        self.required_distance_to_ball_for_flick = 180
        self.offset_bias = 35

    def utility(self, bot):
        car_to_ball = bot.info.my_car.pos - bot.info.ball.pos

        bouncing_b = bot.info.ball.pos[2] > 130 or abs(bot.info.ball.vel[2]) > 300
        if not bouncing_b:
            return 0

        dist_01 = rlmath.clamp01(1 - norm(car_to_ball) / 3000)

        head_dir = rlmath.lerp(vec3(0, 0, 1), bot.info.my_car.forward(), 0.1)
        ang = angle_between(head_dir, car_to_ball)
        ang_01 = rlmath.clamp01(1 - ang / (math.pi / 2))
        on_my_side_b = (sgn(bot.info.ball.pos[1]) == bot.tsgn)

        ball_landing_pos = bot.info.ball.next_landing().data
        tile = tiles.point_to_tile(bot.info, ball_landing_pos)
        protect_tile_b = (tile != None and tile.team == bot.team and
                          (tile.state == tiles.Tile.OPEN or bot.info.ball.team != bot.team))

        return rlmath.clamp01(0.3 * on_my_side_b
                              + 0.3 * ang_01
                              + 0.3 * dist_01
                              + 0.8 * protect_tile_b
                              - 0.3 * bot.analyzer.team_mate_has_ball_01
                              + self.is_dribbling * self.extra_utility_bias)

    def execute(self, bot):
        bot.renderer.draw_string_3d(bot.info.my_car.pos, 1, 1, "AirDrag", bot.renderer.purple())
        self.is_dribbling = True

        ball_landing = bot.info.ball.next_landing()
        tile = tiles.point_to_tile(bot.info, ball_landing.data)

        # Decide on target pos and speed
        if tile != None and tile.team != bot.team and tile.state == tiles.Tile.OPEN:
            # It will hit enemy open tile - so don't save
            target = ball_landing.data
            speed = norm(target - bot.info.my_car.pos) / 2.0
        else:
            target = ball_landing.data - self.offset_bias * bot.analyzer.best_target_dir
            dist = norm(target - bot.info.my_car.pos)
            speed = 1400 if ball_landing.time == 0 else dist / ball_landing.time

        # Do a flick?
        car_to_ball = bot.info.ball.pos - bot.info.my_car.pos
        dist = norm(car_to_ball)
        if dist <= self.required_distance_to_ball_for_flick:
            self.flick_timer += 0.016666
            if self.flick_timer > self.wait_before_flick:
                bot.plan = DodgeTowardsPlan(bot.analyzer.best_target_tile.location, self.flick_init_jump_duration)
        else:
            self.flick_timer = 0

            # dodge on far distances
            if dist > 2300 and speed > 1410:
                ctt_n = normalize(target - bot.info.my_car.pos)
                vtt = dot(bot.info.my_car.vel, ctt_n) / dot(ctt_n, ctt_n)
                if vtt > 750:
                    bot.plan = DodgeTowardsPlan(target)

        self.drive.car = bot.info.my_car
        self.drive.target_pos = target
        self.drive.target_speed = speed
        self.drive.step(0.016666)
        bot.controls = self.drive.controls

    def reset(self):
        self.is_dribbling = False
        self.flick_timer = 0


class Dribble:
    def __init__(self, bot):
        self.drive = Drive(None, None, 0)

    def utility(self, bot):
        ball_height_01 = (bot.info.ball.pos[2] - 100) / 500
        ball_vert_vel_01 = abs(bot.info.ball.vel[2]) / 500
        return max(0, 0.65
                   - 0.5 * ball_height_01
                   - 0.2 * ball_vert_vel_01
                   - 0.3 * bot.analyzer.team_mate_has_ball_01)

    def execute(self, bot):
        bot.renderer.draw_string_3d(bot.info.my_car.pos, 1, 1, "Dribble", bot.renderer.pink())

        ball = bot.info.ball
        car = bot.info.my_car
        aim = bot.analyzer.best_target_tile.location

        car_to_ball = ball.pos - car.pos
        ctb_n = normalize(car_to_ball)
        dist = norm(car_to_ball) - 100
        vel_delta = ball.vel - car.vel
        vel_d = norm(vel_delta)
        time = max(0, dist / (1.5 * vel_d)) if vel_d != 0 else 0
        bvel = norm(ball.vel)

        ball_to_aim_n = normalize(aim - ball.pos)

        nbp = DropshotBall(ball).step_ds(time).pos
        target = nbp - 120 * ball_to_aim_n
        dist_t = norm(target - car.pos)
        speed = min(rlmath.lerp(1.3 * bvel, 2300, dist_t / 1000), 2300)

        bot.renderer.draw_line_3d(ball.pos, nbp, bot.renderer.green())
        bot.renderer.draw_rect_3d(nbp, 10, 10, True, bot.renderer.green())
        bot.renderer.draw_rect_3d(target, 10, 10, True, bot.renderer.pink())

        self.drive.car = bot.info.my_car
        self.drive.target_pos = target
        self.drive.target_speed = speed
        self.drive.step(0.016666)
        bot.controls = self.drive.controls


class QuickAerial:
    def __init__(self, bot):
        self.aerial = None
        self.drive = None
        pass

    def utility(self, bot):
        ball = bot.info.ball
        if ball.pos[2] < 1000:
            return 0

        car = bot.info.my_car
        if car.boost < 30:
            return 0

        car_to_ball = ball.pos - car.pos
        ctb_flat = vec3(car_to_ball[0], car_to_ball[1], 0)
        ang = angle_between(ctb_flat, car.forward())
        if ang > 1:
            return 0

        vf = norm(car.vel)
        if vf < 800:
            return 0

        return 0.8

    def execute(self, bot):
        bot.renderer.draw_string_3d(bot.info.my_car.pos, 1, 1, "Aerial", bot.renderer.red())

        self.aerial = Aerial(bot.info.my_car, vec3(0, 0, 0), 0)
        ball = DropshotBall(bot.info.ball)

        for i in range(60):
            ball.step_ds(0.016666)
            self.aerial.target = ball.pos
            self.aerial.t_arrival = ball.t
            # Check if we can reach it by an aerial
            if self.aerial.is_viable():
                # One more step
                ball.step_ds(0.016666)
                self.aerial.target = ball.pos + vec3(0, 0, 15)
                self.aerial.t_arrival = ball.t
                break

        if self.aerial.is_viable():
            bot.plan = AerialPlan(bot.info.my_car, self.aerial.target, self.aerial.t_arrival)

        self.drive = Drive(bot.info.my_car, bot.info.ball.pos, 2300)
        self.drive.step(0.016666)
        bot.controls = self.drive.controls


class FixOrientation:
    def __init__(self, bot):
        self.aerial_turn = None

    def utility(self, bot):
        return not bot.info.my_car.on_ground

    def execute(self, bot):
        bot.renderer.draw_string_3d(bot.info.my_car.pos, 1, 1, "Recovery", bot.renderer.blue())

        if self.aerial_turn == None:
            self.aerial_turn = AerialTurn(bot.info.my_car)

        self.aerial_turn.step(0.016666)
        bot.controls = self.aerial_turn.controls

    def reset(self):
        self.aerial_turn = None