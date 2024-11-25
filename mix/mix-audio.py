from pydub import AudioSegment

speech = AudioSegment.from_file("speech.wav")
ambience = AudioSegment.from_file("ambience.mp3")

# Normalize format: sample rate, channels
speech = speech.set_frame_rate(44100).set_channels(2)
ambience = ambience.set_frame_rate(44100).set_channels(2)

# Adjust volume (in dB)
speech = speech + 5
ambience = ambience - 20

# Mix audio files
mixed = speech.overlay(ambience)

# Export the result with consistent bit depth
mixed.export("..\stream\RAW\mixed_audio.wav", format="wav", parameters=["-acodec", "pcm_s16le"])

