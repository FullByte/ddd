# Stream Audio

Audio formats ideal for stream are e.g. MP3 or AAC.
We will create audio-chucks in various lengths depending on the program and content.

In `convert_to_HLS.py` we divides the audio chunks into smaller segments and generates a playlist file (.m3u8) to stream sequentially.
This can be done with ffmpeg as follows:

```sh
ffmpeg -i input.mp3 -codec: copy -hls_time 10 -hls_playlist_type vod stream.m3u8
```

Access a stream created by `serve_HLS_stream.py` via:

<http://localhost:8000/hls/ddd/stream.m3u8>
