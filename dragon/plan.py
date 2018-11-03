

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
