from  whisper_infer.events import LogEvent, Enveloppe
from whisper_infer.workers import WorkerManager

class StreamManager:
    def __init__(self):
        self._sinks = []          # callables : CLI, WebSocket, fichier...
        self._orchestrator = None  # référence for on demand snapshot

    def attach_orchestrator(self, orchestrator):
        self._orchestrator = orchestrator

    def subscribe(self, manager: WorkerManager):
        manager.subscribe_to_logs(self._on_event)

    def add_sink(self, fn: callable):
        self._sinks.append(fn)

    def _on_event(self, event: LogEvent):
        # enriched with current snapshot
        snapshot = self._orchestrator.snapshot(event.name) if self._orchestrator else None
        envelope = Enveloppe(event=event, pipeline_state=snapshot)
        for sink in self._sinks:
            sink(envelope)