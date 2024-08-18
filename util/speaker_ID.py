import torch
import yaml
import datetime
from pyannote.audio import Pipeline
from pathlib import Path
from pydub import AudioSegment
from collections import Counter


device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() and torch.backends.mps.is_built() else "cpu")

with open("support_files/config.yaml", 'r') as file:
    configuration = yaml.safe_load(file)

# Accessing the configuration values
base_url = configuration['base_url']
api_key = configuration['api_key']
model_name = configuration['model_name']
hf_token = configuration['hf_token']
database = configuration['database']

# Initialize the PyAnnote pipeline
print(datetime.datetime.now())
pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=hf_token)    
pipeline.to(device)
print(datetime.datetime.now())

# Step 2: Determine the number of speakers by counting files in "Recordings"
recordings_folder = Path("sample_recordings")
sample_files = list(recordings_folder.glob("*.wav"))
  
# Step 3: Bind incoming recording with samples and return the duration information as a dictionary
def bind_recordings(incoming_file, sample_files):
    # Initialize the duration dictionary
    duration_dict = {}

    # Load the incoming recording
    incoming_audio = AudioSegment.from_file(incoming_file)
    
    # Get the duration of the incoming recording in seconds
    incoming_duration = len(incoming_audio) / 1000.0  # Convert milliseconds to seconds
    duration_dict['incoming'] = [0, incoming_duration]  # The start is 0, and the end is the duration
    
    # Initialize the combined audio with the incoming audio
    combined_audio = incoming_audio
    current_end_time = incoming_duration
    
    # Concatenate it with each sample recording and update the duration dictionary
    for i, sample_file in enumerate(sample_files):
        sample_audio = AudioSegment.from_file(sample_file)
        sample_duration = len(sample_audio) / 1000.0  # Convert milliseconds to seconds
        start_time = current_end_time
        end_time = start_time + sample_duration
        duration_dict[sample_file.stem] = [start_time, end_time]
        combined_audio += sample_audio
        current_end_time = end_time
    
    # Save the combined audio
    combined_audio_file = "by_product/combined_audio.wav"
    combined_audio.export(combined_audio_file, format="wav")
    
    return combined_audio_file, duration_dict

# Step 4: Perform diarization
def perform_diarization(combined_audio_file, num_speakers, pipeline):

    # Perform diarization
    diarization = pipeline(combined_audio_file, num_speakers=num_speakers)
    
    return diarization

# Step 5: Identify the label of the incoming audio based on the diarization result.
def majority_vote(labels):
    """Return the most common label using majority voting."""
    if not labels:
        return None
    return Counter(labels).most_common(1)[0][0]

def determine_labels(diarization_result, duration_dict):
    """Determine the label for each interval in the diarization result using majority voting."""
    interval_labels = {}
    
    for interval_name, (start, end) in duration_dict.items():
        labels = []
        for segment, _, label in diarization_result.itertracks(yield_label=True):
            # Check if the segment overlaps with the current interval
            if segment.end > start and segment.start < end:
                labels.append(label)
        
        # Determine the majority label for this interval
        interval_labels[interval_name] = majority_vote(labels)
    
    return interval_labels

def find_incoming_label(interval_labels):
    """Find the interval that shares the same label as 'incoming'."""
    incoming_label = interval_labels['incoming']
    
    for name, label in interval_labels.items():
        if name != 'incoming' and label == incoming_label:
            return name
    
    return None

# Step 6: A wrapper function that intake an incoming_audio, then return the speaker based on given sample recordings
def who_is_the_speaker(incoming_audio, sample_files):
    # Number of speakers
    n = len(sample_files)
    
    combined_audio_file = bind_recordings(incoming_audio, sample_files)
    diarization_result = perform_diarization(combined_audio_file[0], n, pipeline)
    interval_labels = determine_labels(diarization_result, combined_audio_file[1])
    speaker = find_incoming_label(interval_labels)
    
    return(speaker) 