from dotenv import load_dotenv
from openai import OpenAI
from midjourney import *
from voiceover import *
from gpt4 import *
load_dotenv()
import json
import os


# Create API objects gpt4 and midjpourney
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
gpt4 = gpt4API(
    api_key=os.environ.get('OPENAI_API_KEY'),
    client=client,
    story=os.environ.get('STORY_PATH'),
    story_prompt_file_path=os.environ.get('STORY_PROMPT_FILE_PATH'),
    story_results_file_path=os.environ.get('STORY_RESULTS_FILE_PATH'),
    choose_image_prompt_file_path=os.environ.get('CHOOSE_IMAGE_PROMPT_FILE_PATH')
    
)
midjourney = MidjourneyApi(
    application_id=os.environ.get('APPLICATION_ID'), 
    guild_id=os.environ.get('GUILD_ID'), 
    channel_id=os.environ.get('CHANNEL_ID'), 
    version=os.environ.get('VERSION'), 
    id=os.environ.get('ID'), 
    authorization=os.environ.get('AUTHORIZATION')
)
voiceover = elevenlabsAPI(
    api_key=os.environ('ELEVENLABS_API_KEY'),
    voice_id=os.environ('VOICE_ID'),
    model=os.environ('AUDIO_MODEL'),
    audio_file_path=os.environ('AUDIO_FILE_PATH'),
    story_path=os.environ('STORY_PATH'),
    transcript_path=os.environ('TRANSCRIPT_PATH')
)

# Segment the story into meaningful sections and provide a prompt
print('Segmenting story...')
image_segment_info = {}
gpt4.generate_segments()
data = gpt4.parse_json_from_file()
segment_keys, bottom_level = gpt4.categorize_keys(data)
for key in list(set(bottom_level)):
    if 'prompt' in key: prompt_key = key 
    elif 'text' in key: text_key = key

# Generate photos for each segment
for key, value in data.items():
    print(f'Starting with chunk {key}...')
    # Generate 4 images from prompt
    midjourney.prompt = value['prompt']
    midjourney.send_message()
    midjourney.get_message()
    midjourney.download_image()
    # Select 1 of 4 generated images
    midjourney.button_option = gpt4.choose_image(
        image_file_path=midjourney.image_path_str, 
        image_prompt=value[prompt_key]
    )    
    # Download the upscaled version from Midjourney
    midjourney.get_message()
    midjourney.choose_images()
    midjourney.download_image()
    # Save each image to its corresponding segment
    image_segment_info[midjourney.image_path_str] = value[text_key]
    
# Write to file
with open('image_segment_info.json', 'w') as json_file:
    json.dump(image_segment_info, json_file)

# Generate and transcribe audio
voiceover.generate_audio()
voiceover.transcribe_to_srt()


