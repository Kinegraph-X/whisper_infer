# Whisper Infer (whisper-pipeline)

> Keyword detection in remote audio streams — any format ffmpeg can read, any language Whisper can transcribe.

Feed it an m3u8 URL (or any ffmpeg-compatible source), a list of keywords, and it will tell you exactly when they were said.

## What it does

1. **Splits** the remote playlist into manageable chunks
2. **Extracts** audio in parallel with ffmpeg
3. **Transcribes** each chunk with Whisper as soon as audio is ready
4. **Matches** keywords against the transcript, with global timestamps
5. **Reports** all occurrences as a structured JSON file

ffmpeg handles the ingestion — HLS, DASH, MPEG-TS, mp4, and anything else it supports. Whisper handles the transcription. The pipeline runs them concurrently so transcription starts before the full download is complete.

## Architecture

The project is built around a few explicit abstractions:

- **WorkerManager** — manages the lifecycle of subprocesses (ffmpeg, Whisper) as Python `Process` objects, with state tracking and structured logging
- **TaskOrchestrator** — sequences tasks into pipelines, resolves dependencies, handles early exit and cancellation policies
- **StreamManager** — pub/sub layer between workers and consumers (CLI output, WebSocket dashboard); the single API boundary for observability
- **FfmpegLogger** — classifies ffmpeg output into events, progress, and headers; rotates log files per worker

Worker stdout is streamed in real time through a central queue — no polling, no buffering surprises.

## Project structure

```
whisper_infer/
├── workers/
│   ├── basic_worker.py       # Process subclass, asyncio stdout reader
│   ├── worker_manager.py     # Lifecycle, state transitions, log dispatch
│   └── worker_monitor.py     # CLI subscriber
├── tasks/
│   ├── task.py               # Task dataclass (declarative)
│   └── task_orchestrator.py  # Pipeline sequencing, cancel policies
├── pipeline/
│   ├── pipeline.py           # Pipeline container
│   ├── pipeline_config.py    # Runtime config (cancellation, parallelism...)
│   └── stream_manager.py     # Pub/sub, snapshot on state change
├── states/
│   ├── worker_state.py
│   ├── worker_context.py
│   └── task_state.py
├── logging/
│   └── ffmpeg_logger.py      # Per-worker rotating logs (events / progress / summary)
└── m3u8/
    └── split_m3u8.py
config.py                     # Runtime config (env + defaults)
constants.py                  # Immutable paths and names
run_pipeline.py               # Entry point
```

## Usage

```bash
python run_pipeline.py <-i m3u8_url> [--match keyword1 keyword2 ...]
```

Results are written to `matches/<channel_name>_matches.json`:

```json
[
  {
    "keyword": "merger",
    "start": 142.3,
    "end": 144.1,
    "global_start": 4342.3,
    "text": "...the merger was announced this morning...",
    "segment_index": 1
  }
]
```

## Configuration

Environment variables (or `.env`):

| Variable | Default | Description |
|---|---|---|
| `SEGMENT_DURATION` | `3600` | Chunk size in seconds |
| `WHISPER_MODEL` | `small` | Whisper model size |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

## Requirements

- Python 3.10+
- ffmpeg (in PATH)
- [Whisper](https://github.com/openai/whisper) or a compatible inference script

```bash
pip install -r requirements.txt
```

## Status

Work in progress. WebSocket dashboard and full cancel policy support are next.