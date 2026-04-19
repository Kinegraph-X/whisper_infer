import threading, subprocess
from whisper_infer.tasks import CancelPolicy, TaskState
from pipeline import Pipeline, PipelineSnapshot, PipelineState
import time

class TaskOrchestrator:
    def __init__(self, cancel_policy=CancelPolicy.CANCEL_PENDING_ONLY):
        self.pipelines = []
        self.cancel_policy = cancel_policy
        self._early_exit = threading.Event()

    def add_pipeline(self, pipeline : Pipeline):
        self.pipelines.append(pipeline)
        self._next_task(pipeline, 0)
        pipeline.started_at = time.local_time()

    def _next_task(self, pipeline : Pipeline, idx : int):
        for task in pipeline[idx:]:
            # allow passing serializable objects
            task.cmd = [str(part) for part in task.cmd]
            success_behavior = lambda: self._on_task_success(pipeline, idx)
            if task.synchronous:
                task.state = TaskState.RUNNING
                pipeline.currently_running = task
                if task.manager:
                    task.manager.addWorker(
                        task.name,
                        task.cmd,
                        success_behavior
                    )
                else:
                    subprocess.run(
                        task.cmd
                    )
                break
            else:
                if task.manager:
                    task.manager.addWorker(
                        task.name,
                        task.cmd,
                        success_behavior
                    )
                    task.state = TaskState.RUNNING
                    pipeline.currently_running = task

    def _on_task_success(self, pipeline: Pipeline, idx: int):
        task = pipeline[idx]
        if task.manager:
            task.manager.remove_worker(task.name)

        if task.after_complete:
            task.after_complete(task.name)

        if type(task.early_exit_on_success) == 'callable':
            if task.early_exit_on_success():
                self.early_exit()
                return
        elif task.early_exit_on_success:
            self.early_exit()
            return

        next_idx = idx + 1
        if next_idx >= len(pipeline.tasks):
            pipeline.state = PipelineState.DONE
            return

        # vérifier si early_exit a été déclenché entre temps
        if self._early_exit.is_set():
            next_task = pipeline.tasks[next_idx]
            if next_task.cancellable:
                next_task.state = TaskState.CANCELLED
                return

        self.next_task(pipeline, next_idx)

    def snapshot(self, name : str):
        for pipeline in self.pipelines:
            if pipeline.currently_running.name == name:
                return PipelineSnapshot(
                    pipeline.tasks,
                    pipeline.early_exit,
                    pipeline.started_at,
                    time() - time.time(pipeline.started_at)
                )

    def early_exit(self):
        # cancel pending tasks, let running tasks go to end"""
        self._early_exit.set()
        for pipeline in self.pipelines:
            for task in pipeline.values():
                if task.state == TaskState.PENDING and task.cancellable:
                    task.state = TaskState.CANCELLED
                elif task.state == TaskState.RUNNING:
                    if self.cancel_policy == CancelPolicy.CANCEL_ALL:
                        task.manager.stop_worker(task.name)
            pipeline.early_exit = True
            pipeline.state = PipelineState.DONE