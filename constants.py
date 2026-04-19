from typing import Pattern, Match
import os, re
from dataclasses import dataclass
from config import config

@dataclass
class constants():
    # test_m3u8 = "https://d3stzm2eumvgb4.cloudfront.net/bc733ae995ff381d29a9_chez_lex_316364448611_1774793065/360p30/index-muted-2JB1OVSCE2.m3u8"
    test_m3u8 = "https://demo.unified-streaming.com/k8s/features/stable/video/tears-of-steel/tears-of-steel.ism/tears-of-steel-audio_eng=128002-video_eng=1001000.m3u8"
    ffmpeg_logs_folder = "ffmpeg_logs"
    chunks_folder = "chunks/"
    playlists_folder = "playlist/"
    playlist_basename = 'playlist_'
    playlist_ext = 'm3u8'
    audio_file = f"output_audio_{config.channel_name}"
    audio_ext = ".m4a"
    transcripts_folder = "transcripts"
    transcript_file = f"transcript_{config.channel_name}"
    transcript_ext = ".tsv"
    keywords_pattern : Pattern | None = re.compile(r"\b(" + "|".join(config.keywords) + r")\b", re.IGNORECASE) if config.keywords else None
    matching_script = 'runners/match_keywords.py'

os.makedirs(constants.ffmpeg_logs_folder, exist_ok=True)
os.makedirs(constants.chunks_folder, exist_ok=True)
os.makedirs(constants.transcripts_folder, exist_ok=True)
os.makedirs(constants.playlists_folder, exist_ok = True)