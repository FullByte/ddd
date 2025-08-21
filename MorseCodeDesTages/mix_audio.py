#!/usr/bin/env python3
import subprocess
import datetime
import sys
import os

def make_uno_oracle(intro="audio_input/Intro.mp3", message="audio_input/morse.wav", bg="audio_input/morse-bg.mp3"):
    # Output filename with current date
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    out_file = f"{date_str}_morse_code.mp3"

    # FFmpeg command
    cmd = [
        "ffmpeg", "-hide_banner", "-y",
        "-i", intro,
        "-i", message,
        "-stream_loop", "-1", "-i", bg,
        "-filter_complex",
        (
            "[1:a]asetpts=PTS-STARTPTS[voice];"
            "[2:a]volume=0.2,asetpts=PTS-STARTPTS[bgquiet];"
            "[voice][bgquiet]amix=inputs=2:duration=first:dropout_transition=0[mix];"
            "[0:a]asetpts=PTS-STARTPTS[intro];"
            "[intro][mix]acrossfade=d=1:c1=tri:c2=tri[final]"
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
        make_uno_oracle()
    except subprocess.CalledProcessError as e:
        print("FFmpeg failed:", e, file=sys.stderr)
        sys.exit(1)
