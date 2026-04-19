import sys, re
import argparse
from config import config
from constants import constants

parser = argparse.ArgumentParser(
    description='Parallelized, worker-based, transcription and matching engine (via Fast-Whisper) \n' \
    'Usage: python run_pipeline.py <m3u8_url> [-match] [keyword1] [keyword2...]')

parser.add_argument('--debug', 
					help='This will enable CLI logging, instead of using the HTTP server',
                    required=False,
                    action='store_true'
                    )
parser.add_argument('--test', 
					help='This will use test m3u8 urls and mock whisper',
                    required=False,
                    action='store_true'
                    )
parser.add_argument('--dist', 
					help='This will define the paths of the modules relative to the dist folder',
                    required=False,
                    action='store_true'
                    )
parser.add_argument('--path', '-i',
					help='This will define the path to the video/audio/m3u8/manifest file',
                    required=False,
                    nargs='+'
                    )
parser.add_argument('--match', '-m',
					help='This will enable matching on keywords. You must add space separated keywords',
                    required=False,
                    nargs='+'
                    )
parser.add_argument('--chunk_size', '-t',
					help='This will define the size of a chunk when processing audio',
                    required=False,
                    type = 'int',
                    default = 3600
                    )

args = parser.parse_args()

# if args.h:
#     print("Usage: python run_pipeline.py <m3u8_url> [-match] [keyword1] [keyword2...]")

if args.test:
    config.USE_MOCK = True
    config.USE_TEST = True
    config.should_match = False
    config.whisper_path = "whisper_mock.py"

if not args.path:
    config.media_path = constants.test_m3u8
    config.channel_name = "test_channel"
else:
    config.media_path = args.path[0]
    match = re.search(r"/[a-f0-9]+_(.+?)(_\d+)_\d+/", args.path)
    if not match:
        print("Channel name not found, exiting...")
        sys.exit()
    else:
        config.channel_name = match.group(1) + match.group(2)

if args.match:
    config.keywords = args.match
else:
    print(f"[INFO] : matching is not enabled, transcript only")


config.segment_duration = args.chunk_size