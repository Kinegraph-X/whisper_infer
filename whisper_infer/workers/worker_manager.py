import sys, multiprocessing, threading
from worker_logger import WorkerLogger
from multiprocessing import get_context
# if getattr(sys, 'frozen', False):

# ctx = get_context('spawn')  # Explicitly get a new context with 'spawn'
if __name__ == "__main__":
    multiprocessing.freeze_support()
    multiprocessing.set_start_method('spawn', force=True)

from whisper_infer.utils import args as cmd_line_args

from whisper_infer.states import WorkerState
from basic_worker import BasicWorker

# curl -d "{\"name\" : \"server\"}" -H "Content-Type:application/json" -X POST http://localhost:3001/start_worker

class WorkerManager:
    def __init__(self, max_count = 4):
        self.workers = {}
        # self.message_queues = {}
        self._message_queue = multiprocessing.Queue()
        self.on_log_cbs = {}
        self.max_count = max_count
        self._dispatch_thread = threading.Thread(
            target=self._dispatch_loop, daemon=True
        )
        self._dispatch_thread.start()

    def _assert_transition(self, name, required_state):
        worker = self.workers.get(name)
        if not worker:
            raise RuntimeError(f"unknown worker : {name}")
        if worker.context.state != required_state:
            raise RuntimeError(f"worker state mismatch {name} : state {worker.context.state.value}, expected {required_state.value}")
            
    def add_worker(self, name, args_list, on_success : callable = None, on_log : callable = None, *args):
        if len(self.workers) < self.max_count:
            self.reset_worker_instance(name, args_list, on_success, *args)
            if on_log:
                self.on_log_cbs[name] = on_log
        else:
            raise RuntimeError(f'unable to add a new worker : max count reached')
        return self.start_worker(name, *args)

    def reset_worker_instance(self, name, args_list, on_success, *args):
        self.workers[name] = BasicWorker(name, args_list, on_success, debug = cmd_line_args.debug, dist = cmd_line_args.dist)
        self.message_queues[name] = self.workers[name].print_queue
        self.workers[name].ctx.set_stopped("initial state")

    def subscribe_to_logs(self, name, cb):
        self.on_log_cbs[name] = cb

    def start_worker(self, name, *args):
        self._assert_transition(name, WorkerState.STOPPED)
        self.workers[name].start()
        self.workers[name].ctx.set_started("start worker")
        return self.format_status(name, f"{self.workers[name].state.value}")

    def stop_worker(self, name):
        self._assert_transition(name, WorkerState.RUNNING)

        worker = self.workers[name]
        worker.terminate()
        worker.state = WorkerState.STOPPED
        status_obj = self.format_status(name, f"{name} {worker.state.value}")
        self.reset_worker_instance(name)
        return status_obj
        
    def join_worker(self, name):
        self._assert_transition(name, WorkerState.RUNNING)
        worker = self.workers.get(name)
        worker.join()
        if worker.is_alive():
            raise RuntimeError(f"{name} still alive after join")

    def remove_worker(self, name):
        self._assert_transition(name, WorkerState.STOPPED)
        worker = self.workers[name]
        worker.terminate()
        worker.ctx.set_stopped('worker sopped and removed')
        status_obj = self.format_status(name, f"{name} {worker.state.value}")
        self.workers.pop(name)
        return status_obj

    def all_stopped(self):
        return all(w.ctx.state != WorkerState.RUNNING 
                for w in self.workers.values())

    def get_worker_status(self, name):
        worker = self.workers.get(name)
        if not worker:
            return self.format_status(name, f"ERROR : {name} : No instance available for Worker")

        if worker.ctx.state == WorkerState.RUNNING and not worker.is_alive():
            worker.ctx.set_error("Worker wasn't alive when getting status")
        return self.format_status(name, f"{worker.state.value}")

    def format_status(self, name, status_string):
        # Get the messages in the queue (non-blocking)
        messages = []
        queue = self.message_queues[name]
        try:
            while not queue.empty():
                messages.append(queue.get_nowait())
        except:
            pass
        return {
            "status": f"{status_string}",
            "message_stack": messages
        }
    
    # def react_on_msg(self):
    #     while True:
    #         for name, worker in self.workers:
    #             cb = self.on_log_cbs[name]
    #             if not cb:
    #                 continue
    #             if worker.queue_flag.wait(timeout = .1):
    #                 cb(self.message_queues[name])
    #                 worker.queue_flag.clear()

    
    def _dispatch_loop(self):
        while True:
            event = self._message_queue.get()
            if event is None:
                return
            for worker, cb in self.on_log_cbs:
                if event.worker == worker:
                    cb(event)

    def destroy(self):
        self._message_queue.put(None)  # poison pill
        self._dispatch_thread.join()
