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
    def __init__(self):
        self.drive = None
        pass

    def utility(self, bot):
        return 1

    def execute(self, bot):
        if self.drive == None:
            self.drive = Drive(bot.info.my_car, bot.info.ball.pos, 1410)
        bot.action = self.drive
        bot.action.step(0.01666)
        bot.controls = bot.action.controls
        return True

