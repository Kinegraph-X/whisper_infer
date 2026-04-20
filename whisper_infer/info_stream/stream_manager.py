from  whisper_infer.events import LogEvent, Enveloppe, EventType
from whisper_infer.workers import WorkerManager
from whisper_infer.session import SessionManager

class StreamManager:
    def __init__(self, session : SessionManager):
        self._sinks = []          # callables : CLI, WebSocket, fichier...
        self._orchestrator = session.orchestrateur
        self._session = session  # référence for on demand snapshot

    def attach_orchestrator(self, orchestrator):
        self._orchestrator = orchestrator

    def subscribe(self, manager: WorkerManager):
        manager.subscribe_to_logs(self._on_event)
        self._orchestrator.subscribe(self._on_event)

    def add_sink(self, fn: callable):
        self._sinks.append(fn)

    def _on_event(self, event: LogEvent):
        envelope = Enveloppe(event=event)
        if event.type in (EventType.STATE_CHANGE, EventType.TASK_DONE, EventType.EARLY_EXIT):
            # enriched with current snapshot
            envelope.snapshot = self._session.snapshot()
        
        for sink in self._sinks:
            sink(envelope)