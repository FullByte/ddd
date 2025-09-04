#!/usr/bin/env python3
import subprocess
import datetime
import sys
import os
import random

def make_wetter_bericht():
    # Zufällig zwischen intro1 und intro2 wählen
    intro_choice = random.choice(["audio_input/intro1.mp3", "audio_input/intro2.mp3"])
    wetterbericht = "audio_input/wetterbericht.mp3"
    bg = "audio_input/wetter-bg.mp3"
    
    # Output filename with current date
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    out_file = f"{date_str}_wetter_bericht.mp3"

    # FFmpeg command
    cmd = [
        "ffmpeg", "-hide_banner", "-y",
        "-i", intro_choice,
        "-i", wetterbericht,
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

    print(f"Using intro: {intro_choice}")
    print("Running FFmpeg...")
    subprocess.run(cmd, check=True)
    print(f"Created: {out_file}")

if __name__ == "__main__":
    try:
        make_wetter_bericht()
    except subprocess.CalledProcessError as e:
        print("FFmpeg failed:", e, file=sys.stderr)
        sys.exit(1)
