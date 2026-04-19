from dataclasses import dataclass
import time
from whisper_infer.workers import WorkerContext, WorkerManager
from task_snapshot import TaskSnapshot

@dataclass
class ManagedTask:
    name: str
    context: WorkerContext      # état métier
    manager: WorkerManager              # mécanique d'exécution
    snapshot: TaskSnapshot      # état observable

    def refresh_snapshot(self):
        self.snapshot.state = self._derive_state()
        self.snapshot.elapsed = time.time() - self.snapshot.started_at