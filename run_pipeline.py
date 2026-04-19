from config import config
from constants import constants
from whisper_infer.commands import get_ffmpeg_commands
from whisper_infer.tasks import Task, TaskOrchestrator
from whisper_infer.utils import args, get_duration, FloatAccumulator
from whisper_infer.pipeline import  PipelineConfig, PipelineStatus, Pipeline
from whisper_infer.m3u8 import split_m3u8
from whisper_infer.workers import WorkerManager
from whisper_infer.info_stream import StreamManager


# Worker managers
dl_worker_manager = WorkerManager()
whisper_worker_manager = WorkerManager()
stream_manager = StreamManager()
stream_manager.subscribe(dl_worker_manager)
stream_manager.subscribe(whisper_worker_manager)
stream_manager.add_sink(lambda e: print(f"[{e.worker_name}] {e.message}"))

orchestrator = TaskOrchestrator()

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
    orchestrator.add_pipeline(
        Pipeline(
            Task(
                cmd.worker_name,
                dl_worker_manager,
                cmd.cmd,
                True,
                ffmpeg_after_complete
            ),
            Task(
                cmd.transcript_file,
                whisper_worker_manager,
                ['python', config.whisper_actual, cmd.audio_filepath, cmd.transcript_filename],
                True
            ),
            Task(
                f'match_{cmd.transcript_file}',
                None,
                ['python', constants.matching_script, cmd.transcript_filename, current_audio_timestamp],
                True
            )
        )
    )