from threading import Thread, Event
import time

class WhisperMonitor(Thread):
    def __init__(self, whisper_manager, whisper_tasks, process_func, external_stop_event, interval = 1):
        super.__init__()
        self.whisper_manager = whisper_manager
        self.whisper_tasks = whisper_tasks
        self.process_func = process_func
        self.external_stop_event = external_stop_event
        self.interval = interval
        self._stop_event = Event()

    def stop(self):
        self._stop_event.set()

    def run(self):
        while not self._stop_event.is_set():
            self.process()
            time.sleep(self.interval)

    def process(self):
        if self.external_stop_event.is_set() and self.whisper_manager.all_stopped():
            self.stop()
        else:
            self.process_func(self.whisper_manager, self.whisper_tasks)