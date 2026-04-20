from typing import List
from dataclasses import dataclass

@dataclass
class PendingTask:
    name : str
    args_list : List[str]
    on_success : callable
    on_failure : callable