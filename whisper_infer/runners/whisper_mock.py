# whisper_mock.py
import sys
import time
import random
import csv

input_audio = sys.argv[1]
output_tsv = sys.argv[2]

# ⏱️ simule temps de traitement (ex: 5 à 15 sec)
sleep_time = random.uniform(5, 15)

def export_transcription():
    print(f"[MOCK] Processing {input_audio} for {sleep_time:.1f}s")
    start = time.time()
    while time.time() - start < sleep_time:
        _ = sum(i*i for i in range(10000))

    # 📝 génère faux transcript
    with open(output_tsv, "w", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["start", "end", "text"])

        t = 0
        for i in range(10):
            duration = random.uniform(3, 10)
            text = random.choice([
                "hello world",
                "nothing interesting",
                "bitcoin is pumping",
                "random speech here",
                "crypto market analysis"
            ])
            writer.writerow([t, t + duration, text])
            t += duration

    print(f"[MOCK] Done {input_audio}")