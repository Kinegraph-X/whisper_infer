from dataclasses import dataclass
from cancel_policy import CancelPolicy

@dataclass
class PipelineConfig:
    early_exit_on_match: bool = False
    cancel_policy: CancelPolicy = CancelPolicy.CANCEL_PENDING_ONLY
    whisper_max_workers: int = 2
    monitor_interval: float = 1.0
    log_level: str = "INFO"