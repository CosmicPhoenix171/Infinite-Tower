import time


class Timer:
    """
    A utility class for timing operations and measuring elapsed time.
    
    This class provides functionality to start, stop, reset, and measure
    elapsed time, useful for game timing, animations, and performance monitoring.
    """
    
    def __init__(self):
        self.start_time = 0
        self.elapsed_time = 0
        self.running = False

    def start(self):
        """Start the timer if it's not already running."""
        if not self.running:
            self.start_time = self.current_time()
            self.running = True

    def stop(self):
        """Stop the timer and accumulate elapsed time."""
        if self.running:
            self.elapsed_time += self.current_time() - self.start_time
            self.running = False

    def reset(self):
        """Reset the timer to zero, maintaining running state."""
        self.elapsed_time = 0
        if self.running:
            self.start_time = self.current_time()

    def current_time(self):
        """Get the current system time in seconds."""
        return time.time()

    def get_elapsed_time(self):
        """Get the total elapsed time in seconds."""
        if self.running:
            return self.elapsed_time + (self.current_time() - self.start_time)
        return self.elapsed_time