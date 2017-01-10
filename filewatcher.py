import interval
import os

class FileWatcher():
    def __init__(self, filename, sec, on_update):
        self.filename = filename
        self.on_update = on_update
        self.ivl = interval.Interval(self.file_peek, sec)
        self.last_mtime = 0
        self.file_peek()

    def cancel(self):
        self.ivl.cancel()

    def file_peek(self):
        s = os.stat(self.filename)
        if s.st_mtime != self.last_mtime:
            self.on_update(self.filename, s.st_mtime)
            self.last_mtime = s.st_mtime
            