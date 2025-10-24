class Scheduler:
    def __init__(self):
        self.timed_events = []

    def add_event(self, event, delay):
        self.timed_events.append((event, delay))

    def update(self, delta_time):
        for event, delay in self.timed_events:
            delay -= delta_time
            if delay <= 0:
                event()
                self.timed_events.remove((event, delay))