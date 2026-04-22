import urllib.request
import re
from urllib.parse import urljoin

def split_m3u8(input_url, dest_folder, base_filename = 'playlist_', target_duration=3600):
    with urllib.request.urlopen(input_url) as response:
        content = response.read().decode("utf-8")

    lines = content.splitlines(keepends=True)

    chunks = []
    current_chunk = []
    current_duration = 0
    chunk_index = 0

    header = []
    i = 0

    # récupérer header (jusqu'au premier segment)
    while i < len(lines) and not lines[i].startswith("#EXTINF"):
        header.append(lines[i])
        i += 1

    while i < len(lines):
        line = lines[i]

        if line.startswith("#EXTINF"):
            duration = float(line.split(":")[1].split(",")[0])

            newline = '\n'    # python < 3.12 : f-string expression part cannot include a backslash
            lines[i + 1] = re.sub(r"-unmuted\.ts$", "-muted.ts", lines[i+1])
            segment_block = [line, f'{urljoin(input_url, lines[i + 1])}{newline}']

            if current_duration + duration > target_duration and current_chunk:
                # flush chunk
                chunks.append((chunk_index, current_chunk))
                chunk_index += 1
                current_chunk = []
                current_duration = 0

            current_chunk.extend(segment_block)
            current_duration += duration

            i += 2
        else:
            i += 1

    # dernier chunk
    if current_chunk:
        chunks.append((chunk_index, current_chunk))

    # écriture fichiers
    for idx, chunk_lines in chunks:
        filename = f"{dest_folder}{base_filename}{idx:03d}.m3u8"

        with open(filename, "w", encoding="utf-8") as f:
            f.writelines(header)
            f.write("#EXT-X-ENDLIST\n")
            f.writelines(chunk_lines)

    return len(chunks)