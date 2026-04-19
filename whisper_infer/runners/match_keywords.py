import os, sys, re, csv, json
from config import config
from constants import constants

if len(sys.argv) < 3:
    print('usage : python match_keywords <transcript_filename> <start_timestamp>')
    sys.exit()

matches = []

def process_transcript(transcript_filename, start_timestamp):
    print(f"4️⃣ Recherche mots-clés dans {transcript_filename}...")
    with open(transcript_filename, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")

        for row in reader:
            text = row["text"].lower()

            if constants.keywords_pattern.search(text):
                local_start = float(row["start"])
                local_end = float(row["end"])

                # 🔥 conversion en timestamp global
                global_start = start_timestamp + local_start
                global_end = start_timestamp + local_end

                matches.append({
                    "keyword": constants.keywords_pattern.search(text).group(0),
                    "start": local_start,
                    "end": local_end,
                    "global_start": global_start,
                    "global_end": global_end,
                    "text": row["text"],
                    "start_timestamp": start_timestamp
                })
                return True
        return False

process_transcript(sys.argv[1], sys.argv[2])

# store to disk
filename = f"{config.channel_name}_matches.json"
if os.path.exists(filename):
    with open(filename, "r", encoding="utf-8") as f:
        content = json.load(f)
else:
    content = []

content.extend(matches)

with open(filename, "w", encoding="utf-8") as f:
    json.dump(content, f, indent=4, ensure_ascii=False)