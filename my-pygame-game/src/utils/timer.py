class Timer:
    def __init__(self):
        self.start_time = 0
        self.elapsed_time = 0
        self.running = False

    def start(self):
        if not self.running:
            self.start_time = self.current_time()
            self.running = True

    def stop(self):
        if self.running:
            self.elapsed_time += self.current_time() - self.start_time
            self.running = False

    def reset(self):
        self.elapsed_time = 0
        if self.running:
            self.start_time = self.current_time()

    def current_time(self):
        import time
        return time.time()

    def get_elapsed_time(self):
        if self.running:
            return self.elapsed_time + (self.current_time() - self.start_time)
        return self.elapsed_time