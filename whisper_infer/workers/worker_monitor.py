import threading
import time
import sys

class WorkerMonitor(threading.Thread):
    def __init__(self, manager, interval=1.0):
        super().__init__()
        self.manager = manager
        self.interval = interval
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def run(self):
        while not self._stop_event.is_set():
            self.print_status()
            time.sleep(self.interval)

    def print_status(self):
        for name in self.manager.workers.keys():
            status = self.manager.get_worker_status(name)

            # Format propre pour stdout
            line = f"[{name}] {status['status']}"
            
            if status["message_stack"]:
                messages = " \n".join(status["message_stack"])
                line += f" -> {messages}"

            print(line)
        
#        print("-" * 40)
        sys.stdout.flush()