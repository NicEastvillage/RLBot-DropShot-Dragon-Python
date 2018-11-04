from RLUtilities.LinearAlgebra import vec3
from RLUtilities.Maneuvers import Drive


class UtilitySystem:
    def __init__(self, choices, prev_bias=0.15):
        self.choices = choices
        self.current_best_index = -1
        self.prev_bias = prev_bias

    def evaluate(self, bot):
        best_index = -1
        best_score = 0
        for i, ch in enumerate(self.choices):
            score = ch.utility(bot)
            if i == self.current_best_index:
                score += self.prev_bias  # was previous best choice bias
            if score > best_score:
                best_score = score
                best_index = i

        if best_index != self.current_best_index and self.current_best_index != -1:
            # Check if choice has a reset method, then call it
            reset_method = getattr(self.choices[self.current_best_index], "reset", None)
            if callable(reset_method):
                reset_method()

        # New choice
        self.current_best_index = best_index
        return self.choices[self.current_best_index], best_score

    def reset(self):
        self.current_best_index = -1


class AtbaChoice:
    def __init__(self, bot):
        self.drive = Drive(bot.info.my_car, vec3(0, 0, 0), 0)

    def utility(self, bot):
        return 0.5

    def execute(self, bot):
        bot.renderer.draw_string_3d(bot.info.my_car.pos, 1, 1, "Atba", bot.renderer.white())
        self.drive.car = bot.info.my_car
        self.drive.target_pos = bot.info.ball.pos
        self.drive.target_speed = 1500
        self.drive.step(0.01666)
        bot.controls = self.drive.controls
