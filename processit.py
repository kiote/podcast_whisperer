import subprocess
import os
import sys
import torch
from pydub import AudioSegment
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer
import soundfile as sf

def time_to_seconds(time_str):
    time_str = time_str.strip()
    if ':' in time_str:
        parts = time_str.split(':')
        if len(parts) == 3:  # HH:MM:SS.mmm
            hours, minutes, seconds = parts
            return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
        elif len(parts) == 2:  # MM:SS.mmm
            minutes, seconds = parts
            return int(minutes) * 60 + float(seconds)
    else:
        # Assume it's already in seconds
        return float(time_str)

def parse_subtitle_file(file_path):
    segments = []
    with open(file_path, 'r') as f:
        for line in f:
            if line.strip() and line[0] == '[':
                time_range, text = line.strip().split(']')
                start, end = map(time_to_seconds, time_range[1:].split('-->'))
                segments.append((start, end, text.strip()))
    return segments

def create_tts_audio(text, filename, model, tokenizer, device):
    description = "Jon's voice is monotone regular speed in delivery, with a very close recording"
    input_ids = tokenizer(description, return_tensors="pt").input_ids.to(device)
    prompt_input_ids = tokenizer(text, return_tensors="pt").input_ids.to(device)
    
    generation = model.generate(input_ids=input_ids, prompt_input_ids=prompt_input_ids)
    audio_arr = generation.cpu().numpy().squeeze()
    
    sf.write(filename, audio_arr, model.config.sampling_rate)

def extract_audio_segment(input_file, start_time, end_time, output_file):
    subprocess.run([
        'ffmpeg', '-i', input_file, '-ss', str(start_time), 
        '-to', str(end_time), '-c', 'copy', output_file
    ])

def create_silent_audio(duration, filename):
    silent = AudioSegment.silent(duration=duration * 1000)  # pydub works in milliseconds
    silent.export(filename, format="wav")

def combine_audio_files(file_list, output_file):
    subprocess.run(['ffmpeg', '-i', "concat:" + "|".join(file_list), '-acodec', 'copy', output_file])

def main(original_audio, transcription_file, translation_file, output_file):
    device = "cpu"

    model = ParlerTTSForConditionalGeneration.from_pretrained("parler-tts/parler-tts-mini-v1").to(device)
    tokenizer = AutoTokenizer.from_pretrained("parler-tts/parler-tts-mini-v1")

    transcription = parse_subtitle_file(transcription_file)
    translation = parse_subtitle_file(translation_file)

    temp_files = []
    for i, (start, end, orig_text) in enumerate(transcription):
        # Extract original audio segment
        orig_segment = f"temp_orig_{i}.wav"
        extract_audio_segment(original_audio, start, end, orig_segment)
        temp_files.append(orig_segment)

        # Create silence
        silence = f"temp_silence_{i}.wav"
        create_silent_audio(2, silence)
        temp_files.append(silence)

        # Create TTS for translation
        tts_file = f"temp_tts_{i}.wav"
        create_tts_audio(translation[i][2], tts_file, model, tokenizer, device)
        temp_files.append(tts_file)

        # Add another silence
        temp_files.append(silence)

    # Combine all audio files
    combine_audio_files(temp_files, output_file)

    # Clean up temporary files
    for file in temp_files:
        os.remove(file)

if __name__ == "__main__":
    original_audio = "last.mp3"
    transcription_file = "transcribe.txt"
    translation_file = "translated.txt"
    output_file = "final_output.mp3"
    
    main(original_audio, transcription_file, translation_file, output_file)
