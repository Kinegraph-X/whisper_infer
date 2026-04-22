from enum import Enum

class PipelineState(Enum):
    PENDING = "pending"
    RUNNING = "running"
    FAILED =  "failed"
    DONE = "done"
