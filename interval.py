from threading import Timer

class Interval():
    def __init__(self, func, sec):
        self.func = func
        self.sec = sec
        self.timer = None
        self.start()

    def start(self):
        self.timer = Timer(self.sec, self.execute)
        self.timer.start()

    def execute(self):
        self.func()
        self.start()

    def cancel(self):
        self.timer.cancel()
