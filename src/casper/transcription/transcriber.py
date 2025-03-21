import os
import time
import torch
from faster_whisper import WhisperModel
import csv
import json

class Transcriber:
    """A class to handle audio transcription using faster-whisper"""
    
    def __init__(self, model_size="tiny", device=None, compute_type=None):
        """
        Initialize the transcriber with the specified model and device settings
        
        Args:
            model_size: Size of the Whisper model to use (default: "tiny")
            device: Device to use for inference ("cuda" or "cpu")
            compute_type: Compute type for the model ("float16" for GPU, "int8" for CPU)
        """
        # Determine device if not specified
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        # Determine compute type if not specified
        if compute_type is None:
            self.compute_type = "float16" if self.device == "cuda" else "int8"
        else:
            self.compute_type = compute_type
            
        self.model_size = model_size
        self.model = None
        
    def load_model(self):
        """Load the Whisper model"""
        print(f"Loading {self.model_size} model on {self.device} with {self.compute_type}...")
        model_start = time.time()
        
        self.model = WhisperModel(
            self.model_size,
            device=self.device,
            compute_type=self.compute_type,
        )
        
        model_load_time = time.time() - model_start
        print(f"Model loaded in {model_load_time:.2f} seconds")
        
    def transcribe(self, audio_path):
        """
        Transcribe the audio file at the given path
        
        Args:
            audio_path: Path to the audio file to transcribe
            
        Returns:
            Dictionary containing the transcription results and metadata
        """
        if self.model is None:
            self.load_model()
            
        print(f"Transcribing: {audio_path}")
        
        try:
            # Transcribe the audio
            transcribe_start = time.time()
            segments, info = self.model.transcribe(audio_path, word_timestamps=True)
            segments = list(segments)
            transcribe_time = time.time() - transcribe_start
            
            # Build the result
            result = {
                "filename": os.path.basename(audio_path),
                "duration": 0,  # Will be updated if segments exist
                "language": info.language,
                "language_probability": float(info.language_probability),
                "transcription": "",
                "segments": [],
                "processing_time": transcribe_time,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "model": self.model_size,
                "device": self.device
            }
            
            # Process segments
            full_text = ""
            for segment in segments:
                result["segments"].append({
                    "start": float(segment.start),
                    "end": float(segment.end),
                    "text": segment.text
                })
                full_text += segment.text + " "
                
                # Update duration based on the last segment's end time
                if float(segment.end) > result["duration"]:
                    result["duration"] = float(segment.end)
            
            result["transcription"] = full_text.strip()
            
            return result
            
        except Exception as e:
            print(f"ERROR during transcription: {str(e)}")
            return {
                "filename": os.path.basename(audio_path),
                "error": str(e),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
