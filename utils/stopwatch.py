import time


class Stopwatch:
    def __init__(self, start_time=0):
        self.start_time = None
        self.end_time = None
        self.speed = 1
        self.interval = start_time

    def start(self, speed=None):
        if self.start_time is not None and self.end_time is not None:
            self.interval += self.speed * (self.end_time - self.start_time)
            self.start_time = self.end_time = None
        if self.start_time is None:
            self.start_time = time.time()
            if speed is not None:
                self.speed = speed

    def set_speed(self, speed):
        if self.start_time is not None and self.end_time is not None:
            self.interval += self.speed * (self.end_time - self.start_time)
        elif self.start_time is not None and self.end_time is None:
            current = time.time()
            self.interval += self.speed * (current - self.start_time)
            self.start_time = current
        self.speed = speed

    def stop(self):
        if self.start_time is None:
            return
        self.end_time = time.time()

    def is_running(self):
        return self.start_time is not None and self.end_time is None

    def get_time(self):
        """return the passed time in seconds"""
        if self.start_time is None:
            return self.interval
        elif self.end_time is None:
            return self.speed * (time.time() - self.start_time) + self.interval
        return self.speed * (self.end_time - self.start_time) + self.interval

    def get_str_time(self):
        """MINUTE:SECOND:1/100SECOND"""
        time_in_seconds = self.get_time()
        minutes = int(time_in_seconds) // 60
        seconds = int(time_in_seconds) - minutes * 60
        decimals = int((time_in_seconds - int(time_in_seconds)) * 100)
        return f'{minutes:02}:{seconds:02}:{decimals:02}'

    def clear(self):
        self.start_time = None
        self.end_time = None
        self.interval = 0
