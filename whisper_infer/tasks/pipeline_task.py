import time
from typing import List
from dataclasses import dataclass
from whisper_infer.tasks import TaskState
from whisper_infer.workers import WorkerContext, WorkerManager
from task_snapshot import TaskSnapshot
from task import Task
from task_strategy import ExecutionStrategy, LocalProcessStrategy, SubprocessStrategy

@dataclass
class PipelineTask:
    def __init__(self, task_spec : Task, session_id : str = 'local'):
        session_prefix = session_id[:6]
        self.name = f"{session_prefix}_{task_spec.name}"
        self.manager: WorkerManager = task_spec.workerManager
        self.cmd: List[str] = task_spec.cmd
        self.strategy : ExecutionStrategy  = task_spec.synchronous
        self.early_exit_on_success : bool | callable = task_spec.early_exit_on_success
        self.after_complete : callable | None = task_spec.after_complete
        self.cancellable: bool = task_spec.cancellable
        self.context: WorkerContext      # état métier
        self.state: TaskState = TaskState.PENDING
        self.last_error : str = ''
        self.on_success: callable = None
        self.on_failure: callable = None
        self.on_cancel: callable = None

    def snapshot(self):
        return TaskSnapshot(
            self.name,
            self.state,
            self.started_at,
            time.time() - self.started_at if self.started_at else 0,
            self.last_error
        )