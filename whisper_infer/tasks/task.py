import time
from typing import List
from dataclasses import dataclass
from whisper_infer.tasks import TaskState, ExecutionStrategy, LocalProcessStrategy
from whisper_infer.workers import WorkerContext, WorkerManager
from task_snapshot import TaskSnapshot

@dataclass
class Task:
    name: str
    manager: WorkerManager      # mécanique d'exécution
    cmd: List[str]
    strategy : ExecutionStrategy = LocalProcessStrategy
    early_exit_on_success : bool | callable = False
    after_complete : callable | None = None
    cancellable: bool = True
