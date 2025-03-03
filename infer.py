from faster_whisper import WhisperModel

import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA device count: {torch.cuda.device_count()}")

jfk_path = "sample4.opus"
#jfk_path = "speech_orig.wav"
model = WhisperModel(
    "tiny", 
    device="cuda",
    compute_type="float16",
    #device_index=0
)
segments, info = model.transcribe(jfk_path, word_timestamps=True)
for segment in segments:
    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))