from elevenlabs import generate, save, set_api_key
import whisper

class elevenlabsAPI():
    def __init__(self, api_key, voice_id, model, audio_file_path, story_path, transcript_path):
        set_api_key(api_key)
        self.voice_id = voice_id
        self.model = model
        self.audio_file_path = audio_file_path
        self.story = story_path
        self.transcript = transcript_path
    
    def generate_audio(self):
        audio = generate(self.story, voice=self.voice_id, model=self.model)
        save(audio, self.audio_file_path)

    def format_time(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        return f"{hours:02}:{minutes:02}:{seconds:06.3f}".replace('.', ',')

    def create_srt_file(self, transcription, output_file):
        """ Create an SRT file from the transcription """
        with open(output_file, "w") as file:
            for i, segment in enumerate(transcription["segments"]):
                start = self.format_time(segment["start"])
                end = self.format_time(segment["end"])
                file.write(f"{i + 1}\n")
                file.write(f"{start} --> {end}\n")
                file.write(f"{segment['text']}\n\n")

    def transcribe_to_srt(self):
        model = whisper.load_model(model_size='base')
        result = model.transcribe(self.audio_file_path)
        self.create_srt_file(result, output_file=self.transcript)