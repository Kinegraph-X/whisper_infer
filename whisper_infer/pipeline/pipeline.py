import time
from uuid import uuid4
from typing import List
from dataclasses import dataclass
from whisper_infer.tasks import PipelineTask, Task
from pipeline_state import PipelineState
from pipeline_snapshot import PipelineSnapshot

class Pipeline():
    def __init__(self, session_id : str = 'local'):
        self.id : str = uuid4()
        self.session_id = session_id
        self.tasks : List[Task] = []
        self._task_names = set()  # enforce local unicity
        self.state : PipelineState = PipelineState.PENDING
        self.currently_running : Task | None = None
        self.started_at : float = time.time()
        self.early_exit : bool = False

    def add_task(self, task_spec : Task):
        task = PipelineTask(task_spec, self.session_id)
        if task.name in self._task_names:
            raise ValueError(f"Task name '{task.name}' already exists in this pipeline")
        self._task_names.add(task.name)
        self.tasks.append(task)
        return 
    
    def snapshot(self) -> PipelineSnapshot | None:
        return PipelineSnapshot(
            pipeline_id=self.pipeline_id,
            tasks=[t.snapshot() for t in self.tasks],
            state=self.state,
            early_exit = self.early_exit,
            started_at=self.started_at,
            elapsed=time.time() - self.started_at if self.started_at else 0
        )