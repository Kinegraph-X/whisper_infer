import time
from typing import List
from dataclasses import dataclass
from whisper_infer.tasks import TaskState
from whisper_infer.workers import WorkerContext, WorkerManager
from task_snapshot import TaskSnapshot

@dataclass
class Task:
    name: str
    manager: WorkerManager      # mécanique d'exécution
    cmd: List[str]
    synchronous : bool  = False
    early_exit_on_success : bool | callable = False
    after_complete : callable | None = None
    cancellable: bool = True
    context: WorkerContext      # état métier
    snapshot: TaskSnapshot      # état observable
    state: TaskState = TaskState.PENDING
    # depends_on: list = field(default_factory=list)
    on_success: callable = None
    on_failure: callable = None
    on_cancel: callable = None

    def refresh_snapshot(self):
        self.snapshot.state = self._derive_state()
        self.snapshot.elapsed = time.time() - self.snapshot.started_at