from dotenv import load_dotenv
from openai import OpenAI
from midjourney import *
from voiceover import *
from video import *
from gpt4 import *
load_dotenv()
import json
import time
import os


# Create API objects gpt4 and midjpourney
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
video = VideoProcesser()
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
    api_key=os.environ.get('ELEVENLABS_API_KEY'),
    voice_id=os.environ.get('VOICE_ID'),
    model=os.environ.get('AUDIO_MODEL'),
    audio_file_path=os.environ.get('AUDIO_FILE_PATH'),
    story_path=os.environ.get('STORY_PATH'),
    transcript_path=os.environ.get('TRANSCRIPT_PATH'),
    image_segment_info=os.environ.get('IMAGE_SEGMENT_INFO'),
    presenter_voice_id=os.environ.get('PRESENTER_VOICE_ID'),
    story_question_file_path=os.environ.get('STORY_QUESTION_FILE_PATH')
)


def segment_story(generate_new):
    # Segment the story into meaningful sections and provide a prompt
    print('Segmenting story...')
    if generate_new: 
        gpt4.generate_segments()
        with open(os.environ.get('IMAGE_SEGMENT_INFO'), 'w') as file:
            json.dump({}, file)
    data = gpt4.parse_json_from_file()
    segment_keys, bottom_level = gpt4.categorize_keys(data)
    for key in list(set(bottom_level)):
        if 'prompt' in key: prompt_key = key 
        elif 'text' in key: text_key = key
    return data, prompt_key, text_key

def generate_images(data, prompt_key, text_key):
    # Read the JSON file and convert it to a Python dictionary
    with open(os.environ.get('IMAGE_SEGMENT_INFO'), 'r') as file:
        saved_data = json.load(file)
    # Continue off where previous run left off (if applicable)
    for key, value in saved_data.items():
        del data[key]
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
        midjourney.custom_id = midjourney.custom_ids[midjourney.button_option-1]
        print(f'Choosing {midjourney.custom_id}')
        midjourney.choose_images()
        midjourney.download_image()
        # Save image and segment info
        save_image_segment_info(key, value, text_key)

def save_image_segment_info(key, value, text_key):
    # Read the existing data
    with open(os.environ.get('IMAGE_SEGMENT_INFO'), 'r') as file:
        data = json.load(file)
    # Save each image to its corresponding segment
    data[key] = [midjourney.image_path_str, value[text_key]]
    # Write to file
    with open(os.environ.get('IMAGE_SEGMENT_INFO'), 'w') as json_file:
        json.dump(data, json_file)


    
    
def user_confirmation():
    while True:
        user_input = input("Do you want to proceed? (yes/no): ").strip().lower()
        if user_input == 'yes':
            print("Continuing...")
            return False
        elif user_input == 'no':
            raise ValueError("Error(main): Script halted by user.")
        else:
            print("Invalid input. Please type 'yes' or 'no'.")

def main():
    # Segment story
    data, prompt_key, text_key = segment_story(generate_new=True)
    user_confirmation()
    
    # Generate images
    generate_images(data, prompt_key, text_key)
    user_confirmation()
        
    # Generate voiceover and transcribe
    voiceover.generate_audio(data, text_key)
    voiceover.transcribe(data.keys())
    user_confirmation()
    
    # Video Processing
    time.sleep(5) # wait for transcript to complete saving
    video.create_video_with_audio()
    
if __name__ == '__main__':
    main()