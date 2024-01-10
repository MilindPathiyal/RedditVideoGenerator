from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip
from PIL import Image, ImageOps
import datetime
import random
import string
import json
import os


class VideoProcesser():
    def __init__(self):
        with open(os.environ.get('TRANSCRIPT_PATH'), 'r') as file:
            self.data = json.load(file)
        self.final_video = ''
        self.screenshot = 'screenshot.png'
        
    def generate_video_title(self):
        # Get today's date
        today_date = datetime.date.today()

        # Generate a random 5-character string
        random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
        self.final_video = os.environ.get('VIDEO_FILE_PATH') + f"{today_date} {random_string}.mp4"
        
        return self.final_video
    
    def add_border_to_screenshot(self, image, scale_factor=0.5):
        """
        Adds a border to an image and returns the path to the new image.

        :param input_path: Path to the original image.
        :param border_size: Size of the border to add.
        :param border_color: Color of the border.
        :return: Path to the new image with border.
        """
        img = Image.open(image)
        bordered_img = ImageOps.expand(img, border=10, fill='black')
        new_size = (int(img.width * scale_factor), int(img.height * scale_factor))
        resized_img = bordered_img.resize(new_size, Image.Resampling.LANCZOS)
        resized_img.save('resized_' + image)
    
    def create_video_with_audio(self):

        output_path = self.generate_video_title()
        audio_paths, image_paths, durations = [], [], []
        for key, val in self.data.items():
            image_paths.append(val[0]) # Get images in chronological order
            audio_paths.append(val[2]) # Get the audio files
            durations.append(val[3]) # Get duration for each scene

        # Create a clip for each image with the specified duration
        combined_clips = []
        for image_path, audio_path in zip(image_paths, audio_paths):
            # Load the image and audio
            image_clip = ImageClip(image_path)
            audio_clip = AudioFileClip(audio_path)

            # Set the duration of the image clip to match the audio clip
            image_clip = image_clip.set_duration(audio_clip.duration)

            # Combine the image and audio clips
            combined_clip = image_clip.set_audio(audio_clip)
            combined_clips.append(combined_clip)
        
        # Concatenate all the combined clips together
        final_video_clip = concatenate_videoclips(combined_clips, method="compose")

        # Get intro audio clip
        intro_audio_clip = AudioFileClip('audio/generated_audio_intro.wav')
        
        # Load the static image and set its duration
        self.add_border_to_screenshot(self.screenshot)
        static_image_clip = ImageClip('resized_' + self.screenshot).set_start(intro_audio_clip.duration).set_duration(final_video_clip.duration - intro_audio_clip.duration)
        video_size = final_video_clip.size
        static_img_size = static_image_clip.size
        position = ((video_size[0] - static_img_size[0]) / 2, video_size[1] - static_img_size[1] - 150)        
        
        # Load the static question image and set its duration
        self.add_border_to_screenshot('q'+self.screenshot)
        static_image_clip_q = ImageClip('resized_q' + self.screenshot).set_start(0).set_duration(intro_audio_clip.duration)
        final_video = CompositeVideoClip([final_video_clip, static_image_clip_q.set_pos(('center', 'center')), static_image_clip.set_pos(position)])

        # Write the result to a file
        final_video.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24)



