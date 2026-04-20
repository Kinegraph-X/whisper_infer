import time, threading
from uuid import uuid4
from session import Session
from session_snapshot import SessionSnapshot
from whisper_infer.pipeline import PipelineOrchestrator
from whisper_infer.tasks import CancelPoliccy, TaskState, CancelPolicy
from whisper_infer.events import EventType
from whisper_infer.states import SessionState

class SessionManager:
    def __init__(self, cancel_policy=CancelPolicy.CANCEL_PENDING_ONLY):
        self.session : Session | None = None
        self.orchestrator = PipelineOrchestrator(self.session, cancel_policy)

    def create_session(self, config) -> Session:
        self.session = Session(
            uuid4().hew,
            config.media_path,
            config.keywords,
            time.time()
        )

    def stop_session(self):
        self.session.state = SessionState.STOPPING
        self.orchestrator._propagate_state_change(None, None, EventType.STATE_CHANGE)
        
        # annuler les pending, laisser les running
        for pipeline in self.orchestrator.pipelines:
            for task in pipeline.tasks:
                if task.state == TaskState.PENDING and task.cancellable:
                    task.state = TaskState.CANCELLED
        
        # surveiller la fin des running dans un thread
        threading.Thread(target=self._wait_for_stop, daemon=True).start()

    def _wait_for_stop(self):
        while any(
            t.state == TaskState.RUNNING
            for p in self.orchestrator.pipelines
            for t in p.tasks
        ):
            time.sleep(0.5)
        self.session.state = SessionState.DONE
        self.orchestrator._propagate_state_change(None, None, EventType.STATE_CHANGE)

    def cancel_session(self):
        for idx, pipeline in self.pipelines:
            self.orchestrator.stop_pipeline(idx)

    def session_snapshot(self) -> SessionSnapshot:
        return SessionSnapshot(
            session_id=self.session.id,
            media_path=self.session.media_path,
            keywords=self.session.keywords,
            state=self.session.state,
            started_at=self.session.started_at,
            elapsed=time.time() - self.session.started_at if self.session.started_at else 0,
            pipelines=[self.orchestrator.pipeline_snapshot(p.pipeline_id) for p in self.orchestrator.pipelines],
            failure_reasons=self.session.failure_reasons
        )
    