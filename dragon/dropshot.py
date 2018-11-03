import math

from RLUtilities.GameInfo import *
from RLUtilities.LinearAlgebra import dot, cross, norm, normalize

from tiles import ALL_TILES


TO_WALL = 4555
TO_CORNER = 2 * TO_WALL / math.sqrt(3)
TO_CORNER_ROUNDED = 5026
HEIGHT = 2018
GRAVITY = vec3(0, 0, -650)


class DropshotInfo(GameInfo):
    def __init__(self, index, team):
        super().__init__(index, team)

        self.tile_dict = {}
        self.tile_list = ALL_TILES
        for tile in self.tile_list:
            self.tile_dict[tile.hex] = tile

    def read_packet(self, packet):
        super().read_packet(packet)

        for i in range(packet.num_tiles):
            self.tile_list[i].state = packet.dropshot_tiles[i].tile_state


class DropshotBall(Ball):

    RADIUS = 104.0

    def __init__(self, ball):
        super().__init__(ball)

    def arrival_at_height(self, height, dir="ANY"):
        """ Returns if and when the ball arrives at a given height. The dir argument can be set to a string
        saying ANY, DOWN, or UP to specify which direction the ball should be moving when arriving. """
        is_close = abs(height - self.pos[2]) < 2
        if is_close and dir == "ANY":
            return UncertainEvent(True, 0)

        D = 2 * GRAVITY[2] * height - 2 * GRAVITY[2] * self.pos[2] + self.vel[2] ** 2

        # Check if height is above current pos.z, because then it might never get there
        if self.pos[2] < height and dir != "DOWN":
            turn_time = -self.vel[2] / (2 * GRAVITY[2])
            turn_point_height = DropshotBall(self).fall(turn_time).pos[2]

            # Return false if height is never reached or was in the past
            if turn_point_height < height or turn_time < 0 or D < 0:
                return UncertainEvent(False, 1e300)

            # The height is reached on the way up
            return UncertainEvent(True, (-self.vel[2] + math.sqrt(D)) / GRAVITY[2])

        if dir != "UP" and 0 < D:
            # Height is reached on the way down
            return UncertainEvent(True, -(self.vel[2] + math.sqrt(D)) / GRAVITY[2])
        else:
            # Never fulfil requirements
            return UncertainEvent(False, 1e300)

    def arrival_at_any_wall(self):
        index = -1
        earliest = 100000
        for i, wall in enumerate(ALL_WALLS):
            wall_hit_event = wall.next_ball_hit(self)
            if wall_hit_event.happens and wall_hit_event.time <= earliest:
                index = i
                earliest = wall_hit_event.time
        if index == -1:
            return UncertainEvent(False, 1e300, vec3(0, 0, 1))
        return UncertainEvent(True, earliest, ALL_WALLS[index].normal)

    def fall(self, time, g=GRAVITY):
        self.pos = 0.5 * g * time * time + self.vel * time + self.pos
        self.vel = g * time + self.vel
        return self

    def bounce_off(self, normal):
        # See https://samuelpmish.github.io/notes/RocketLeague/ball_bouncing/
        # For dropshot the slip velocity becomes zero after the first bounce, so chips model is slightly tweaked
        MU = 0.285
        CR = 0.605

        v_perp = normal * dot(self.vel, normal)
        v_para = self.vel - v_perp
        v_spin = cross(normal, self.omega) * DropshotBall.RADIUS

        s = v_para - v_spin
        delta_v_para = vec3(0, 0, 0)
        if norm(s) != 0:

            delta_v_para = -MU * s

        delta_v_perp = v_perp * -(1.0 + CR)

        self.vel += delta_v_perp + delta_v_para
        self.omega = cross(self.vel, normal) * (1. / DropshotBall.RADIUS)
        return self

    def step_ds(self, time):
        if time <= 0:
            return self

        limit = 30
        time_spent = 0

        while time - time_spent > 0.002 and limit >= 0:
            limit -= 1
            time_left = time - time_spent

            wall_hit_event = self.arrival_at_any_wall()
            ground_hit_event = self.arrival_at_height(DropshotBall.RADIUS + 2.5 - 2, "DOWN")

            # Check if ball hit anything
            if ground_hit_event.happens_after_time(time_left) and wall_hit_event.happens_after_time(time_left):
                return self.fall(time_left)

            elif wall_hit_event.happens_before(ground_hit_event):
                # Move ball until it hits wall
                time_spent += wall_hit_event.time
                self.fall(wall_hit_event.time)
                self.bounce_off(wall_hit_event.data)

            elif ground_hit_event.time < 0.1 and abs(self.vel[2]) < 13.0:

                # Ball is rolling. Move it until it hits wall or out of time
                self.vel = vec3(self.vel[0], self.vel[1], 0)

                if not wall_hit_event.happens:
                    # Ball is laying still
                    return self

                if time_left < wall_hit_event.time:
                    # Out of time happens first, just roll
                    return self.fall(time, g=vec3(0, 0, 0))

                # Roll to wall
                time_spent += wall_hit_event.time
                self.fall(wall_hit_event.time, g=vec3(0, 0, 0))
                self.bounce_off(wall_hit_event.data)

            else:
                # Move ball to ground hit or to time out if ball is below floor level
                t = time_left if not ground_hit_event.happens else min(time_left, ground_hit_event.time)
                time_spent += t
                self.fall(t)
                self.bounce_off(vec3(0, 0, 1))

        if limit < 0:
            print("Limit was reached!")

        return self


class Wall:
    def __init__(self, anchor, normal):
        self.anchor = anchor
        self.normal = normalize(normal)
        self.offset_anchor = anchor + DropshotBall.RADIUS * self.normal

    def next_ball_hit(self, ball):
        """ Returns if and when the given ball will hit this wall. """
        dot_vel = dot(ball.vel, self.normal)
        if dot_vel == 0:
            return UncertainEvent(False, 1e300)
        dist = ball.pos - self.offset_anchor
        time = (self.normal[0] * dist[0] + self.normal[1] * dist[1]) / -dot_vel
        return UncertainEvent(0 < time, time)


class Ceiling:
    def __init__(self):
        self.normal = vec3(0, 0, -1)

    def next_ball_hit(self, ball):
        """ Returns if and when the given ball will hit this ceiling. """
        return ball.arrival_at_height(HEIGHT - DropshotBall.RADIUS, dir="UP")


ORANGE_BACK_WALL = Wall(vec3(0, TO_WALL, 0), vec3(0, -1, 0))
BLUE_BACK_WALL = Wall(vec3(0, -TO_WALL, 0), vec3(0, 1, 0))

NORTH_WEST_WALL = Wall(vec3(TO_CORNER, 0, 0), vec3(-TO_WALL, -0.5 * TO_CORNER_ROUNDED, 0))
NORTH_EAST_WALL = Wall(vec3(-TO_CORNER, 0, 0), vec3(TO_WALL, -0.5 * TO_CORNER_ROUNDED, 0))
SOUTH_EAST_WALL = Wall(vec3(-TO_CORNER, 0, 0), vec3(TO_WALL, 0.5 * TO_CORNER_ROUNDED, 0))
SOUTH_WEST_WALL = Wall(vec3(TO_CORNER, 0, 0), vec3(-TO_WALL, 0.5 * TO_CORNER_ROUNDED, 0))

CEILING = Ceiling()

ALL_WALLS = [ORANGE_BACK_WALL,
             BLUE_BACK_WALL,
             NORTH_WEST_WALL,
             NORTH_EAST_WALL,
             SOUTH_EAST_WALL,
             SOUTH_WEST_WALL,
             CEILING]


class UncertainEvent:
    def __init__(self, happens, time, data=None):
        self.happens = happens
        self.time = time
        self.data = data

    def happens_before_time(self, time):
        return self.happens and self.time < time

    def happens_before(self, other):
        return (self.happens and not other.happens) or (other.happens and self.happens_before_time(other.time))

    def happens_after_time(self, time):
        return not self.happens or self.time > time

    def happens_after(self, other):
        return self.happens and (not other.happens or other.time < self.time)