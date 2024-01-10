import json
import base64
import requests
import re


class gpt4API():
    def __init__(self, api_key, client, story, story_prompt_file_path, story_results_file_path, choose_image_prompt_file_path):
        
        self.client=client
        self.api_key=api_key
        self.story = story
        self.story_prompt_file_path=story_prompt_file_path
        self.story_results_file_path=story_results_file_path
        self.choose_image_prompt=choose_image_prompt_file_path
        self.reply_content = ''
        
    def generate_segments(self):
        user_input = self.read_user_input()
        completion = self.client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {
                    "role": "system", 
                    "content": "You are an excellent storyteller possesses imagination, creativity, understanding of narrative structure, character development skills, emotional intelligence, descriptive abilities, good pacing, engaging presentation, adaptability, listening skills, cultural awareness, passion, enthusiasm, and a strong command of language."
                },
                {
                    "role": "user", 
                    "content": user_input
                }
            ]
        )
        self.reply_content = completion.choices[0].message.content
        self.write_results()    
        
    def read_user_input(self):
        with open(self.story_prompt_file_path, 'r') as file:
            user_input = file.read()
        with open(self.story, 'r') as file:
            story = file.read()
        user_input += story
        return user_input
    
    def write_results(self):
        with open(self.story_results_file_path, "w") as file:
            for result in self.reply_content:
                file.write(result)
    

    def parse_json_from_file(self):
        """
        Parses JSON data embedded within a text file.

        Parameters:
        file_path (str): The path to the file containing the JSON data.

        Returns:
        dict: A dictionary representing the parsed JSON data.
        """
        file_path = self.story_results_file_path
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            
            # Locating the start and end of the JSON data
            is_json='json' if content.find('```json') != -1 else ''
            start = content.find(f'```{is_json}') + len(f'```{is_json}\n')
            end = content.find('```', start)

            # Extracting the JSON part
            json_data = content[start:end].strip()

            # Converting the JSON string to a Python dictionary
            data = json.loads(json_data)
            return data
        
        except Exception as e:
            return f"Error: {e}"
        
    def choose_image(self, image_file_path, image_prompt):
        print('GPT4 choosing an image.')
        # Read prompt 
        with open(self.choose_image_prompt, 'r') as file:
            prompt = file.read()
        prompt += image_prompt
        
        # Encode the image
        with open(image_file_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')

        headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": prompt
                },
                {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
                }
            ]
            }
        ],
        "max_tokens": 300
        }
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        data = response.json()
        content= data['choices'][0]['message']['content']
        # Regular expression to find numbers
        image = re.findall(r'\d+', content)
        print(f'GPT API chose {image[0]}')
        return int(image[0])
        
    
    def categorize_keys(self, nested_dict):
        top_level_keys = []
        second_level_keys = []

        for key, value in nested_dict.items():
            top_level_keys.append(key)
            if isinstance(value, dict):
                second_level_keys.extend(value.keys())

        return top_level_keys, second_level_keys