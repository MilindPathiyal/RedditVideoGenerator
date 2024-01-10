from elevenlabs import generate, save, set_api_key
from pydub import AudioSegment
import json
import os

class elevenlabsAPI():
    def __init__(self, api_key, voice_id, model, audio_file_path, story_path, transcript_path, image_segment_info, presenter_voice_id, story_question_file_path):
        set_api_key(api_key)
        self.voice_id = voice_id
        self.model = model
        self.audio_file_path = audio_file_path
        self.story = story_path
        self.transcript = transcript_path
        self.image_segment_info = image_segment_info
        self.presenter_voice_id = presenter_voice_id
        self.story_question_file_path = story_question_file_path
    
    def generate_audio(self, data, text_key):
        with open(self.story_question_file_path, 'r') as file:
            intro = file.read()
        intro_audio = generate(intro, voice=self.presenter_voice_id, model=self.model)
        intro_audio_file = self.audio_file_path + f'generated_audio_intro.wav'
        save(intro_audio, intro_audio_file)
        
        
        for key, val in data.items():
            audio = generate(val[text_key], voice=self.voice_id, model=self.model)    
            output_audio_file = self.audio_file_path + f'generated_audio_{key}.wav'
            save(audio, output_audio_file)
            
            if '1' in key:
                combined = AudioSegment.empty()
                combined += AudioSegment.from_file(intro_audio_file) + AudioSegment.from_file(output_audio_file)
                combined.export(output_audio_file, format=output_audio_file.split('.')[-1])

    def transcribe(self, keys):
        audio_files = os.listdir(self.audio_file_path)
        audio_files.sort()
        with open(self.image_segment_info, 'r') as file:
            data = json.load(file)
        # Determine length of each audio file
        for file, chunk in zip(audio_files, keys):
            audio = AudioSegment.from_file(self.audio_file_path + file)
            # Calculate the length in milliseconds
            length_ms = len(audio)
            # Convert to seconds
            length_seconds = length_ms / 1000.0
            data[chunk].extend([self.audio_file_path + file, length_seconds])
        # Write to transcript file
        with open(self.transcript, "w") as json_file:
            json.dump(data, json_file)
            
    
    def combine_audio_files(self):
        """
        Combine multiple audio files into a single audio file.

        Parameters:
        file_list (list): List of paths to audio files.
        output_file (str): Path to save the combined audio file.

        Returns:
        str: Path to the combined audio file.
        """
        output_file = self.audio_file_path + os.environ.get('COMBINED_AUDIO_FILE')
        if os.path.exists(output_file):
            # Delete the file
            os.remove(output_file)
        audio_files = os.listdir(self.audio_file_path)
        file_list = [self.audio_file_path + file for file in audio_files]
        file_list.sort()
        combined = AudioSegment.empty()
        for file in file_list:
            audio = AudioSegment.from_file(file)
            combined += audio

        combined.export(output_file, format=output_file.split('.')[-1])
        return output_file