from typing import List, Tuple, Dict, Sequence
from whisper_infer.context import constants, config

def get_ffmpeg_commands(chunks_count : int) -> List[Dict[str, Sequence[str]]]:
    commands = []
    for i in range(chunks_count):
        audio_filepath = f"{constants.chunks_folder}{constants.audio_file}_{i + 1}{constants.audio_ext}"
        transcript_filename = f'{constants.transcript_file}_{i}{constants.transcript_ext}'
        commands.append(
            {
                'audio_filepath' : audio_filepath,
                'cmd' : [
                    "ffmpeg",
                    "-y",    # always confirm overwrite
                    "-protocol_whitelist", "file,http,https,tcp,tls",
                    "-i", f"{constants.playlists_folder}{constants.playlist_basename}{i:03d}.m3u8",
                    "-reset_timestamps", "1",
                    "-vn",
                    "-c", "copy",
                    audio_filepath
                ],
                'worker_name' : f'ffmpeg_{config.channel_name}_{i:03d}',
                'transcript_filename' : transcript_filename
            }
        )
    return commands