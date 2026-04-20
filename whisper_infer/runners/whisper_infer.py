import sys
import json
import torch
import time
import csv
from config import config

from faster_whisper import WhisperModel

if len(sys.argv) < 2:
    print("Usage: python whisper_infer.py <input_audio> [transcript_filename]")
    sys.exit(1)


timestamp = time.strftime('%Y%m%d_%H%M%S')
base_filename = sys.argv[1]
if len(sys.argv) > 2:
    transcript_filename = sys.argv[2]
else:
    transcript_filename = f"{base_filename}_{timestamp}"
model_size = config.whisper_model

# Run on GPU with FP16
model = WhisperModel(model_size, device="cpu", compute_type="int8")

# or run on GPU with INT8
# model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
# or run on CPU with INT8
# model = WhisperModel(model_size, device="cpu", compute_type="int8")

segments, info = model.transcribe(base_filename + ".m4a", beam_size=5)

print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

# for segment in segments:
    # print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))

def export_transcription(segments, base_filename):
    
    tsv_file = f"{transcript_filename}.tsv"
    srt_file = f"{transcript_filename}.srt"

    start_session = time.strftime('%Y-%m-%d %H:%M:%S')

    # --- TSV ---
    with open(tsv_file, "w", encoding="utf-8", newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        
        # header
        writer.writerow(["start", "end", "id", "text"])
        
        for segment in segments:
            writer.writerow([
                round(segment.start, 3),
                round(segment.end, 3),
                segment.id,
                segment.text.strip()
            ])

    # --- SRT ---
    def fmt_time(t):
        h, m = divmod(int(t), 3600)
        m, s = divmod(m, 60)
        ms = int((t % 1) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    with open(srt_file, "w", encoding="utf-8") as f:
        f.write(f"NOTE SESSION START {start_session}\n\n")

        for i, segment in enumerate(segments, 1):
            f.write(f"{i}\n")
            f.write(f"{fmt_time(segment.start)} --> {fmt_time(segment.end)}\n")
            f.write(f"{segment.text.strip()}\n\n")

        f.write(f"NOTE SESSION END {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    print(f"✅ Export OK → {tsv_file} + {srt_file}")

export_transcription(segments, transcript_filename)