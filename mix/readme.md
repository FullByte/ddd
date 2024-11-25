# Mix audio



[pydub](https://github.com/jiaaro/pydub) requires ffmpeg and is a great tool to mix different audio files into one.

It also takes care of audio format differences e.g.:

- Sample Rate (Hz): If the audio files have different sample rates (e.g., 44.1 kHz vs. 48 kHz), pydub will resample them to a common rate for mixing.
- Bit Depth: Differences in bit depth are also normalized by pydub to ensure compatibility.
- Channels: For mono vs. stereo files, pydub will either duplicate or mix down channels as necessary.
