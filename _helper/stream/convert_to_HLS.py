import os
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

UPLOAD_DIR = "RAW"
HLS_DIR = "HLS"

class HLSGenerator(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith((".mp3", ".wav")):
            return

        input_file = event.src_path
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_dir = os.path.join(HLS_DIR, base_name)

        os.makedirs(output_dir, exist_ok=True)
        playlist_path = os.path.join(output_dir, "stream.m3u8")

        # Generate HLS segments and playlist using ffmpeg
        ffmpeg_command = [
            "ffmpeg",
            "-i", input_file,
            "-codec:", "copy",
            "-start_number", "0",
            "-hls_time", "10",                # Segment duration (in seconds)
            "-hls_playlist_type", "vod",
            os.path.join(output_dir, "stream.m3u8")
        ]

        print(f"Processing {input_file} into HLS...")
        subprocess.run(ffmpeg_command)
        print(f"HLS files for {input_file} saved in {output_dir}")

# Set up the directory watcher
if __name__ == "__main__":
    event_handler = HLSGenerator()
    observer = Observer()
    observer.schedule(event_handler, UPLOAD_DIR, recursive=False)
    observer.start()

    print(f"Watching {UPLOAD_DIR} for new audio files...")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
