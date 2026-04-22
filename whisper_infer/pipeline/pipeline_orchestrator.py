from typing import List, Callable
import threading, subprocess, time
from uuid import uuid4

from .pipeline import Pipeline
from .pipeline_snapshot import PipelineSnapshot
from .pipeline_failure import  PipelineFailure

from whisper_infer.states import Pipeline_State
from whisper_infer.tasks import Task, CancelPolicy, TaskState, Session
from whisper_infer.events import LogEvent, EventType

class PipelineOrchestrator:
    def __init__(self, session : Session, cancel_policy=CancelPolicy.CANCEL_PENDING_ONLY):
        self.session : Session | None = None
        self.pipelines : List[Pipeline] = []
        self.cancel_policy = cancel_policy
        self._early_exit = threading.Event()
        self._sink : Callable | None = None

    def add_pipeline(self):
        pipeline = Pipeline()
        self.pipelines.append(pipeline)
        return pipeline.id
    
    def add_task(self, pipeline_id : str, task : Task):
        pipeline = next((p for p in self.pipelines if p.id == pipeline_id), None)
        if not pipeline:
            raise ValueError(f'add_task() on non-existing pipeline. pipeline_id is {pipeline_id}')
        pipeline.add_task(task)

    def start_pipeline(self, pipeline_id : str):
        pipeline = next((p for p in self.pipelines if p.id == pipeline_id), None)
        if not pipeline:
            raise ValueError(f'start_pipeline() on non-existing pipeline. pipeline_id is {pipeline_id}')
        self._next_task(pipeline, 0)
        pipeline.state = PipelineState.RUNNING

    def start_all_pipelines(self):
        for pipeline in self.pipelines:
            self._next_task(pipeline, 0)
            pipeline.state = PipelineState.RUNNING

    def stop_pipeline(self, pipeline_id : str):
        pipeline = next((p for p in self.pipelines if p.id == pipeline_id), None)
        if not pipeline:
            raise ValueError(f'start_pipeline() on non-existing pipeline. pipeline_id is {pipeline_id}')
        for task in pipeline.tasks:
            if task.state == TaskState.PENDING and task.cancellable:
                task.state = TaskState.CANCELLED
            elif task.state == TaskState.RUNNING:
                if self.cancel_policy == CancelPolicy.CANCEL_ALL:
                    task.manager.stop_worker(task.name)
                    task.manager.remove_worker(task.name)
        pipeline.state = PipelineState.STOPPED

    def subscribe(self, on_event : Callable):
        self._sink = on_event

    def _next_task(self, pipeline, idx):
        if idx >= len(pipeline.tasks):
            pipeline.state = PipelineState.DONE
            return

        task = pipeline.tasks[idx]
        task.state = TaskState.RUNNING

        task.strategy.run(
            task,
            on_success=lambda: self._on_task_success(pipeline, idx),
            on_failure=lambda: self._on_task_failure(pipeline, idx)
        )

    def _on_task_success(self, pipeline: Pipeline, idx: int):
        task = pipeline.tasks[idx]
        if task.manager:
            task.manager.remove_worker(task.name)

        # first check if early_exit has bee trigger meanwhile
        next_idx = idx + 1
        if self._early_exit.is_set():
            self._propagate_state_change(task.name, pipeline, EventType.EARLY_EXIT)
            for task in pipeline.tasks[next_idx:]:
                if task.cancellable:
                    task.state = TaskState.CANCELLED
            pipeline.state = PipelineState.DONE
            return

        if task.after_complete:
            task.after_complete(task.name)

        self._propagate_state_change(task.name, pipeline, EventType.STATE_CHANGE)

        if callable(task.early_exit_on_success):
            if task.early_exit_on_success():
                self.early_exit()
                self._propagate_state_change(task.name, pipeline, EventType.EARLY_EXIT)
                return
        elif task.early_exit_on_success:
            self.early_exit()
            self._propagate_state_change(task.name, pipeline, EventType.EARLY_EXIT)
            return

        next_idx = idx + 1
        if next_idx >= len(pipeline.tasks):
            pipeline.state = PipelineState.DONE
            self._propagate_state_change(task.name, pipeline, EventType.STATE_CHANGE)
            return

        self._next_task(pipeline, next_idx)

    def _on_task_failure(self, pipeline: Pipeline, idx: int):
        task = pipeline.tasks[idx]
        task.state = TaskState.FAILED
        pipeline.state = PipelineState.FAILED
        self._on_pipeline_failure(pipeline, f'task {task.name} failed')
        self._propagate_state_change(task.name, pipeline, EventType.STATE_CHANGE)
        if task.manager:
            task.manager.remove_worker(task.name)
        for task in pipeline.tasks[idx + 1:]:
            if task.cancellable:
                task.state = TaskState.CANCELLED
                return

    def _on_pipeline_failure(self, pipeline, reason):
        if self.session:
            self.session.failure_reasons.append(
                PipelineFailure(
                    pipeline.pipeline_id,
                    reason,
                    time.time()
                )
            )

    def _propagate_state_change(self, task_name, pipeline, type):
        if self._sink:
            self._sink( 
                LogEvent(
                    task_name,
                    "",
                    pipeline,
                    type
                )
            )

    def early_exit(self):
        # cancel pending tasks, let running tasks go to end"""
        self._early_exit.set()
        for pipeline in self.pipelines:
            for task in pipeline.tasks:
                if task.state == TaskState.PENDING and task.cancellable:
                    task.state = TaskState.CANCELLED
                elif task.state == TaskState.RUNNING:
                    if self.cancel_policy == CancelPolicy.CANCEL_ALL:
                        task.manager.stop_worker(task.name)
                        task.manager.remove_worker(task.name)
            pipeline.early_exit = True
            pipeline.state = PipelineState.DONE