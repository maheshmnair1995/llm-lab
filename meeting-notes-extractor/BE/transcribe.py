from faster_whisper import WhisperModel

# Load a small model for better speed
model = WhisperModel("small", device="cpu", compute_type="int8")


def transcribe_file(audio_path: str):
    segments, info = model.transcribe(audio_path, beam_size=5)
    transcript = " ".join([segment.text for segment in segments])
    segs = [{"start": s.start, "end": s.end, "text": s.text} for s in segments]
    return transcript, segs
