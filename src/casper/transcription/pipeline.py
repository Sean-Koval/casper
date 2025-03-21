import os
import csv
import argparse
import json
import time
from datetime import datetime
import logging
from tqdm import tqdm
from .transcriber import Transcriber

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class TranscriptionPipeline:
    """
    Pipeline for processing audio files in an input directory structure and 
    outputting transcriptions to a corresponding output directory structure.
    """
    
    def __init__(self, input_dir, output_dir, model_size="tiny", device=None, compute_type=None):
        """
        Initialize the pipeline with input and output directories
        
        Args:
            input_dir: Directory containing person folders with audio files
            output_dir: Directory where output CSVs will be stored
            model_size: Size of the Whisper model to use
            device: Device to use for inference ("cuda" or "cpu")
            compute_type: Compute type for the model ("float16" for GPU, "int8" for CPU)
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        
        # Initialize the transcriber
        self.transcriber = Transcriber(model_size, device, compute_type)
        
        # Supported audio file extensions
        self.supported_extensions = ['.wav', '.opus', '.mp3', '.m4a', '.ogg', '.flac']
        
        # Stats tracking
        self.stats = {
            'total_files_processed': 0,
            'total_duration_seconds': 0,
            'total_processing_time': 0,
            'folders_processed': {},
            'start_time': None,
            'end_time': None,
            'files_with_errors': 0,
            'successful_files': 0
        }
        
    def create_directory(self, path):
        """Create directory if it doesn't exist"""
        if not os.path.exists(path):
            os.makedirs(path)
            logger.info(f"Created directory: {path}")
            
    def is_audio_file(self, filename):
        """Check if the file has a supported audio extension"""
        return any(filename.lower().endswith(ext) for ext in self.supported_extensions)
    
    def process_file(self, audio_path, folder_name):
        """
        Process a single audio file
        
        Args:
            audio_path: Path to the audio file
            folder_name: Name of the folder (used for organizing outputs)
            
        Returns:
            Dictionary with the transcription results
        """
        filename = os.path.basename(audio_path)
        file_start_time = time.time()
        
        logger.info(f"Processing file: {audio_path}")
        
        # Transcribe the audio
        result = self.transcriber.transcribe(audio_path)
        
        # Add file-specific metadata
        result['folder_name'] = folder_name
        result['original_path'] = audio_path
        
        # Update stats
        processing_time = time.time() - file_start_time
        self.stats['total_files_processed'] += 1
        self.stats['total_processing_time'] += processing_time
        
        if 'error' in result:
            self.stats['files_with_errors'] += 1
            logger.error(f"Error processing {filename}: {result['error']}")
        else:
            self.stats['successful_files'] += 1
            self.stats['total_duration_seconds'] += result['duration']
        
        # Update folder-specific stats
        if folder_name not in self.stats['folders_processed']:
            self.stats['folders_processed'][folder_name] = {
                'file_count': 0,
                'audio_duration': 0,
                'processing_time': 0,
                'success_count': 0,
                'error_count': 0
            }
            
        self.stats['folders_processed'][folder_name]['file_count'] += 1
        self.stats['folders_processed'][folder_name]['processing_time'] += processing_time
        
        if 'error' in result:
            self.stats['folders_processed'][folder_name]['error_count'] += 1
        else:
            self.stats['folders_processed'][folder_name]['success_count'] += 1
            if 'duration' in result:
                self.stats['folders_processed'][folder_name]['audio_duration'] += result['duration']
        
        # Add processing time to result
        result['processing_time'] = processing_time
        
        logger.info(f"Finished processing {filename} in {processing_time:.2f}s")
        return result
        
    def process_person_folder(self, person_folder, total_files):
        """
        Process all audio files in a person's folder
        
        Args:
            person_folder: Path to the person's folder
        """
        folder_name = os.path.basename(person_folder)
        folder_start_time = time.time()
        
        logger.info(f"\nProcessing folder: {folder_name}")
        
        # Create corresponding output directory
        person_output_dir = os.path.join(self.output_dir, folder_name)
        self.create_directory(person_output_dir)
        
        # Process all audio files in the folder
        results = []
        audio_file_count = 0
        
        for filename in tqdm(os.listdir(person_folder), desc=f"Processing {folder_name}", total=len(os.listdir(person_folder)), unit="files"):
            file_path = os.path.join(person_folder, filename)
            
            if os.path.isfile(file_path) and self.is_audio_file(filename):
                audio_file_count += 1
                result = self.process_file(file_path, folder_name)
                results.append(result)
                tqdm.write(f"Processed {self.stats['total_files_processed']} files across {self.stats['total_files_processed']} out of {total_files}.")
        # Create a single CSV for the folder with all transcriptions
        if results:
            csv_path = os.path.join(person_output_dir, f"{folder_name}_transcriptions.csv")
            with open(csv_path, 'w', newline='') as csvfile:
                # Dynamic fieldnames based on the first successful result
                # Start with basic fields all results will have
                fieldnames = ['filename', 'transcription', 'error', 'processing_time', 'timestamp']
                
                # Add additional fields from successful results
                for result in results:
                    if 'error' not in result:
                        fieldnames = ['filename', 'transcription', 'language', 'language_probability', 
                                      'duration', 'timestamp', 'processing_time', 'model', 'device', 'segments']
                        break
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for result in results:
                    row = {
                        'filename': os.path.basename(result.get('original_path', '')),
                        'processing_time': f"{result.get('processing_time', 0):.2f}",
                        'timestamp': result.get('timestamp', ''),
                        'error': result.get('error', '')  # Ensure error is always present

                    }
                    
                    if 'error' in result:
                        row['error'] = result['error']
                        row['transcription'] = ''
                    else:
                        # Convert segments to JSON string if available
                        segments_json = ''
                        if 'segments' in result and result['segments']:
                            segments_json = json.dumps(result['segments'])
                        
                        row.update({
                            'transcription': result.get('transcription', ''),
                            'language': result.get('language', ''),
                            'language_probability': f"{result.get('language_probability', 0):.4f}",
                            'duration': f"{result.get('duration', 0):.2f}",
                            'model': result.get('model', ''),
                            'device': result.get('device', ''),
                            'segments': segments_json
                        })
                        
                    writer.writerow(row)
            
            logger.info(f"Created transcriptions CSV with segments at {csv_path}")
            
            # No longer need to write segments to a separate JSON file since they're now in the CSV
        
        folder_processing_time = time.time() - folder_start_time
        
        # Update folder stats with processing time
        if folder_name in self.stats['folders_processed']:
            self.stats['folders_processed'][folder_name]['total_time'] = folder_processing_time
        
        logger.info(f"Folder {folder_name} completed: processed {audio_file_count} files in {folder_processing_time:.2f}s")
        logger.info(f"Created transcriptions CSV at {csv_path}")
        
    def write_master_log(self):
        """Write a master log CSV file with high-level data on all processed folders"""
        master_log_path = os.path.join(self.output_dir, 'master_transcription_log.csv')
        
        with open(master_log_path, 'w', newline='') as csvfile:
            fieldnames = [
                'folder_name', 
                'files_processed', 
                'successful_files', 
                'files_with_errors', 
                'total_audio_duration_sec', 
                'processing_time_sec',
                'real_time_factor',
                'average_time_per_file_sec'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # Sort folders alphabetically
            sorted_folders = sorted(self.stats['folders_processed'].keys())
            
            for folder_name in sorted_folders:
                folder_stats = self.stats['folders_processed'][folder_name]
                
                # Calculate per-folder metrics
                rtf = 0
                avg_time = 0
                
                if folder_stats['audio_duration'] > 0:
                    rtf = folder_stats['processing_time'] / folder_stats['audio_duration']
                
                if folder_stats['file_count'] > 0:
                    avg_time = folder_stats['processing_time'] / folder_stats['file_count']
                
                writer.writerow({
                    'folder_name': folder_name,
                    'files_processed': folder_stats['file_count'],
                    'successful_files': folder_stats['success_count'],
                    'files_with_errors': folder_stats['error_count'],
                    'total_audio_duration_sec': f"{folder_stats['audio_duration']:.2f}",
                    'processing_time_sec': f"{folder_stats['processing_time']:.2f}",
                    'real_time_factor': f"{rtf:.4f}",
                    'average_time_per_file_sec': f"{avg_time:.2f}"
                })
        
        logger.info(f"Wrote master log to {master_log_path}")
    
    def write_summary_stats(self):
        """Write overall summary statistics to a file"""
        stats_path = os.path.join(self.output_dir, 'transcription_summary.txt')
        
        with open(stats_path, 'w') as f:
            # Calculate overall statistics
            total_duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
            folder_count = len(self.stats['folders_processed'])
            
            f.write("="*50 + "\n")
            f.write("TRANSCRIPTION PIPELINE SUMMARY\n")
            f.write("="*50 + "\n")
            f.write(f"Start Time: {self.stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"End Time: {self.stats['end_time'].strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Pipeline Duration: {total_duration:.2f}s\n")
            f.write(f"Folders Processed: {folder_count}\n")
            f.write(f"Total Files Processed: {self.stats['total_files_processed']}\n")
            f.write(f"Successful Files: {self.stats['successful_files']}\n")
            f.write(f"Files With Errors: {self.stats['files_with_errors']}\n")
            
            if self.stats['total_files_processed'] > 0:
                avg_time = self.stats['total_processing_time'] / self.stats['total_files_processed']
                f.write(f"Average Processing Time Per File: {avg_time:.2f}s\n")
            
            if self.stats['total_duration_seconds'] > 0:
                rtf = self.stats['total_processing_time'] / self.stats['total_duration_seconds']
                f.write(f"Overall Real-time Factor: {rtf:.4f}x (lower is better)\n")
                
            f.write("="*50 + "\n")
        
        logger.info(f"Wrote summary statistics to {stats_path}")
        
    def log_stats_summary(self):
        """Log a summary of processing statistics"""
        total_duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
        folder_count = len(self.stats['folders_processed'])
        
        logger.info("\n" + "="*50)
        logger.info("TRANSCRIPTION PIPELINE SUMMARY")
        logger.info("="*50)
        logger.info(f"Start Time: {self.stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"End Time: {self.stats['end_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Total Pipeline Duration: {total_duration:.2f}s")
        logger.info(f"Folders Processed: {folder_count}")
        logger.info(f"Total Files Processed: {self.stats['total_files_processed']}")
        logger.info(f"Successful Files: {self.stats['successful_files']}")
        logger.info(f"Files With Errors: {self.stats['files_with_errors']}")
        
        if self.stats['total_files_processed'] > 0:
            logger.info(f"Average Processing Time Per File: {self.stats['total_processing_time'] / self.stats['total_files_processed']:.2f}s")
        
        if self.stats['total_duration_seconds'] > 0:
            rtf = self.stats['total_processing_time'] / self.stats['total_duration_seconds']
            logger.info(f"Real-time Factor: {rtf:.4f}x (lower is better)")
            
        logger.info("="*50)
        
    def run(self):
        """Run the complete transcription pipeline"""
        self.stats['start_time'] = datetime.now()
        
        logger.info(f"Starting transcription pipeline...")
        logger.info(f"Input directory: {self.input_dir}")
        logger.info(f"Output directory: {self.output_dir}")
        
        # Ensure output directory exists
        self.create_directory(self.output_dir)
        
        # Load the transcription model
        self.transcriber.load_model()

        # Count total number of audio files
        total_files = 0
        for item in os.listdir(self.input_dir):
            person_folder = os.path.join(self.input_dir, item)
            if os.path.isdir(person_folder):
                for filename in os.listdir(person_folder):
                    file_path = os.path.join(person_folder, filename)
                    if os.path.isfile(file_path) and self.is_audio_file(filename):
                        total_files += 1

        # Process each person's folder
        folders_processed = 0
        for item in os.listdir(self.input_dir):
            person_folder = os.path.join(self.input_dir, item)
            
            if os.path.isdir(person_folder):
                folders_processed += 1
                self.process_person_folder(person_folder, total_files)
        
        self.stats['end_time'] = datetime.now()
        
        # Log summary statistics
        self.log_stats_summary()
        
        # Write summary statistics to a text file
        self.write_summary_stats()
        
        # Write the master log CSV
        self.write_master_log()
                
        logger.info(f"\nTranscription pipeline completed! Processed {self.stats['total_files_processed']} files across {folders_processed} folders.")
