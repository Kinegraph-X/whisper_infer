from typing import List
from whisper_infer.context import get_app_context
config, constants = get_app_context()
# import whisper_infer.commands 
from whisper_infer.commands import get_ffmpeg_commands
from whisper_infer.tasks import Task, LocalProcessStrategy, SubprocessStrategy
from whisper_infer.utils import get_duration, FloatAccumulator
from whisper_infer.pipeline import  Pipeline
from whisper_infer.m3u8 import split_m3u8
from whisper_infer.workers import WorkerManager
from whisper_infer.info_stream import StreamManager
from whisper_infer.session import SessionManager


pipelines : List[Pipeline] = []

session_manager = SessionManager(config)

# Worker managers
dl_worker_manager = WorkerManager(session_manager.session.id)
whisper_worker_manager = WorkerManager(session_manager.session.id)

orchestrator = session_manager.orchestrator
stream_manager = StreamManager()
stream_manager.subscribe(dl_worker_manager)
stream_manager.subscribe(whisper_worker_manager)
stream_manager.add_sink(lambda e: print(f"[{e.worker_name}] {e.message}"))

print("1️⃣ Fix & Split playlist...")
chunks_count = split_m3u8(
    config.media_path,
    constants.playlists_folder,
    constants.playlist_basename,
    config.segment_duration
    )
print(f'{chunks_count} chunks created')

current_audio_timestamp = FloatAccumulator()
ffmpeg_after_complete = lambda name: current_audio_timestamp(get_duration(name))

commands = get_ffmpeg_commands(chunks_count)

for cmd in commands:
    pipeline_id = orchestrator.add_pipeline()
    orchestrator.add_task(
        pipeline_id,
        Task(
            cmd.worker_name,
            dl_worker_manager,
            cmd.cmd,
            LocalProcessStrategy(),
            ffmpeg_after_complete
        )
    )
    orchestrator.add_task(
        pipeline_id,
        Task(
            cmd.transcript_filename,
            whisper_worker_manager,
            ['python', config.whisper_actual, cmd.audio_filepath, cmd.transcript_filename],
            LocalProcessStrategy()
        )
    )
    orchestrator.add_task(
        pipeline_id,
        Task(
            f'match_{cmd.transcript_filename}',
            None,
            ['python', constants.matching_script, cmd.transcript_filename, current_audio_timestamp],
            SubprocessStrategy()
        )
    )

orchestrator.start_all_pipelines()
