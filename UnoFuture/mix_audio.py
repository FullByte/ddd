#!/usr/bin/env python3
import subprocess
import datetime
import sys
import os

def make_uno_future(intro="audio_input/intro.mp3", content="audio_input/content_example.mp3", bg="audio_input/uno_bg.mp3", outro="audio_input/outro.mp3"):
    # Output filename with current date
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    out_file = f"{date_str}_uno_future.mp3"

    # FFmpeg command
    cmd = [
        "ffmpeg", "-hide_banner", "-y",
        "-i", intro,
        "-i", content,
        "-stream_loop", "-1", "-i", bg,
        "-i", outro,
        "-filter_complex",
        (
            "[1:a]asetpts=PTS-STARTPTS[voice];"
            "[2:a]volume=0.2,asetpts=PTS-STARTPTS[bgquiet];"
            "[voice][bgquiet]amix=inputs=2:duration=first:dropout_transition=0[mix];"
            "[0:a]asetpts=PTS-STARTPTS[intro];"
            "[3:a]asetpts=PTS-STARTPTS[outro];"
            "[intro][mix]acrossfade=d=1:c1=tri:c2=tri[x1];"
            "[x1][outro]acrossfade=d=1:c1=tri:c2=tri[final]"
        ),
        "-map", "[final]",
        "-ar", "44100",
        "-c:a", "libmp3lame", "-b:a", "192k",
        out_file
    ]

    print("Running FFmpeg...")
    subprocess.run(cmd, check=True)
    print(f"Created: {out_file}")

if __name__ == "__main__":
    try:
        make_uno_future()
    except subprocess.CalledProcessError as e:
        print("FFmpeg failed:", e, file=sys.stderr)
        sys.exit(1)
