import gzip
import hashlib
import os
import textwrap
import requests
import json
import base64
import math
from io import BytesIO
from PIL import Image
from .Util import EncodeImage

# CATEGORY
cat = "Mira/WAI_Character_Select"

current_dir = os.path.dirname(os.path.abspath(__file__))
json_folder = os.path.join(current_dir, "json")

character_list_cn = ''
character_list_en = ''
character_dict = {}

llm_config = {
    "base_url": "https://api.groq.com/openai/v1/chat/completions",
    "model": "llama-3.3-70b-versatile",
    "api_key":"<your API Key not here, go to the settings.json file!!!>"
}

wai_illustrious_character_select_files = [       
    {'name': 'settings', 'file_path': os.path.join(json_folder, 'settings.json'), 'url': 'https://raw.githubusercontent.com/mirabarukaso/ComfyUI_Mira/refs/heads/main/json/settings.json'},
    {'name': 'wai_character', 'file_path': os.path.join(json_folder, 'wai_characters.csv'), 'url':'https://raw.githubusercontent.com/mirabarukaso/character_select_stand_alone_app/refs/heads/main/data/wai_characters.csv'}
]

prime_directive = textwrap.dedent("""\
    You are a Stable Diffusion prompt writer. Follow these guidelines to generate prompts:
    1.Prohibited keywords: Do not use any gender-related words such as "man," "woman," "boy," "girl," "person," or similar terms.
    2.Format: Provide 8 to 16 keywords separated by commas, keeping the prompt concise.
    3.Content focus: Concentrate solely on visual elements of the image; avoid abstract concepts, art commentary, or descriptions of intent.
    4.Keyword categories: Ensure the prompt includes keywords from the following categories:
        - Theme or style (e.g., cyberpunk, fantasy, wasteland)
        - Location or scene (e.g., back alley, forest, street)
        - Visual elements or atmosphere (e.g., neon lights, fog, ruined)
        - Camera angle or composition (e.g., front view, side view, close-up)
        - Action or expression (e.g., standing, jumping, smirk, calm)
        - Environmental details (e.g., graffiti, trees)
        - Time of day or lighting (e.g., sunny day, night, golden hour)
        - Additional effects (e.g., depth of field, blurry background)
    5.Creativity and coherence: Select keywords that are diverse and creative, forming a vivid and coherent scene.
    6.User input: Incorporate the exact keywords from the user's query into the prompt where appropriate.
    7.Emphasis handling: If the user emphasizes a particular aspect, you may increase the number of keywords in that category (up to 6), but ensure the total number of keywords remains between 8 and 16.
    8.Character description: You may describe actions and expressions but must not mention specific character traits (such as gender or age). Words that imply a character (e.g., "warrior") are allowed as long as they do not violate the prohibited keywords.
    9.Output: Provide the answer as a single line of comma-separated keywords.
    Prompt for the following theme:
    """)

def decode_response(response):
    if response.status_code == 200:
        ret = response.json().get('choices', [{}])[0].get('message', {}).get('content', '')
        print(f'[{cat}]:Response:{ret}')
        # Renmove <think> for DeepSeek
        if str(ret).__contains__('</think>'):
            ret = str(ret).split('</think>')[-1].strip()
            print(f'\n[{cat}]:Trimed response:{ret}')    
            
        ai_text = ret.strip()
        if ai_text.endswith('.'):
            ai_text = ai_text[:-1] + ','      
        if not ai_text.endswith(','):
            ai_text = f'{ai_text},'            
        return ai_text    
    else:
        print(f"[{cat}]:Error: Request failed with status code {response.status_code}")
        return []

def llm_send_request(input_prompt, url, model, api_key, system_prompt=prime_directive):
    data = {
            'model': model,
            'messages': [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": input_prompt + ";Response in English"}
            ],  
        }
    response = requests.post(url, headers={"Content-Type": "application/json", "Authorization": "Bearer " + api_key}, json=data, timeout=30)
    return decode_response(response)

class llm_prompt_gen_node:
    '''
    llm_prompt_gen_node
    
    An AI based prpmpte gen node
    
    Optional:
    system_prompt      - System prompt for AI Gen
    
    Input:  
    url                - The url to your Remote AI Gen
    model              - Model select
    prompt             - Contents that you need AI to generate
    random_action_seed - MUST connect to `Seed Generator`
    
    Output:
    ai_prompt          - Prompts generate by AI
    '''
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "optional": {
                "optional_system_prompt": ("STRING", {
                    "display": "input" ,
                    "multiline": True
                }),                      
            },
            "required": {
                "url":("STRING", {
                    "multiline": False,
                    "default": llm_config["base_url"]
                }),
                "model":("STRING", {
                    "multiline": False,
                    "default": llm_config["model"]
                }),
                "prompt": ("STRING", {
                    "display": "input" ,
                    "multiline": True
                }),     
                "random_action_seed": ("INT", {
                    "default": 1024, 
                    "min": 0, 
                    "max": 0xffffffffffffffff,
                    "display": "input"
                }),
            }
        }
        
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("ai_prompt",)
    FUNCTION = "llm_prompt_node_ex"
    CATEGORY = cat
    
    def llm_prompt_node_ex(self, url, model, prompt, random_action_seed, optional_system_prompt=''):
        _ = random_action_seed
        if '' == optional_system_prompt:
            optional_system_prompt = prime_directive
        return (llm_send_request(prompt, url, model, llm_config["api_key"], system_prompt=optional_system_prompt),)

def llm_send_local_request(input_prompt, server, temperature=0.5, n_predict=512, system_prompt=prime_directive):
    data = {
            "temperature": temperature,
            "n_predict": n_predict,
            "cache_prompt": True,
            "stop": ["<|im_end|>"],
            'messages': [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": input_prompt + ";Response in English"}
            ],  
        }
    response = requests.post(server, headers={"Content-Type": "application/json"}, json=data)

    return decode_response(response)

class local_llm_prompt_gen:
    '''
    local_llm_prompt_gen

    An AI based prpmpte gen node for local LLM

    Server args:
    llama-server.exe -ngl 40 --no-mmap -m "F:\\LLM\\Meta-Llama\\GGUF_Versatile-Llama-3-8B.Q8_0\\Versatile-Llama-3-8B.Q8_0.gguf"

    For DeepSeek, you may need a larger n_predict 2048~ and lower temperature 0.4~, for llama3.3 256~512 may enough.

    Optional:
    system_prompt      - System prompt for AI Gen

    Input:
    server             - Your llama_cpp server addr. E.g. http://127.0.0.1:8080/chat/completions
    temperature        - A parameter that influences the language model's output, determining whether the output is more random and creative or more predictable.
    n_predict          - Controls the number of tokens the model generates in response to the input prompt
    prompt             - Contents that you need AI to generate
    random_action_seed - MUST connect to `Seed Generator`

    Output:
    ai_prompt          - Prompts generate by AI
    '''
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "optional": {
                "optional_system_prompt": ("STRING", {
                    "display": "input" ,
                    "multiline": True
                }),                      
            },
            "required": {
                "server": ("STRING", {
                    "default": "http://127.0.0.1:8080/chat/completions", 
                    "display": "input" ,
                    "multiline": False
                }),
                "temperature": ("FLOAT", {
                    "min": 0.1,
                    "max": 1,
                    "step": 0.05,
                    "default": 0.5
                }),
                "n_predict": ("INT", {
                    "min": 128,
                    "max": 4096,
                    "step": 128,
                    "default": 256
                }),
                "prompt": ("STRING", {
                    "display": "input" ,
                    "multiline": True
                }),     
                "random_action_seed": ("INT", {
                    "default": 1024, 
                    "min": 0, 
                    "max": 0xffffffffffffffff,
                    "display": "input"
                }),
            }
        }
        
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("ai_prompt",)
    FUNCTION = "local_llm_prompt_gen_ex"
    CATEGORY = cat
    
    def local_llm_prompt_gen_ex(self, server, temperature, n_predict, prompt, random_action_seed, optional_system_prompt=''):
        _ = random_action_seed
        if '' == optional_system_prompt:
            optional_system_prompt = prime_directive
        return (llm_send_local_request(prompt, server, temperature=temperature, n_predict=n_predict, system_prompt=optional_system_prompt),)     
    
class illustrious_character_select:
    '''
    illustrious_character_select
    
    Inputs:
    character             - Character
    random_action_seed    - MUST connect to `Seed Generator`
    
    Optional Input:
    custom_prompt         - An optional custom prompt for final output. E.g. AI Generated ptompt`
        
    Outputs:
    prompt                - Final prompt
    info                  - Debug info
    '''                       
        
    @classmethod
    def INPUT_TYPES(s):
        
        return {
            "optional": {
                "custom_prompt": ("STRING", {
                    "display": "input" ,
                    "multiline": True
                }),                      
            },
            "required": {
                "character": (character_list_cn, ),
                "random_action_seed": ("INT", {
                    "default": 1024, 
                    "min": 0, 
                    "max": 0xffffffffffffffff,
                    "display": "input"
                }),
                "character_weight": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 2.0, "step": 0.05}),
                "insert_before_character" : ("BOOLEAN", {"default": False}),
            },
        }
                        
    RETURN_TYPES = ("STRING","STRING",)
    RETURN_NAMES = ("prompt", "info",)
    FUNCTION = "illustrious_character_select_ex"
    CATEGORY = cat
    
    def illustrious_character_select_ex(self, character, random_action_seed, character_weight, insert_before_character, custom_prompt = ''):
        chara = ''
        rnd_character = ''
        
        if 'random' == character:
            index = random_action_seed % len(character_list_cn)
            rnd_character = character_list_cn[index]
            if 'random' == rnd_character:
                rnd_character = character_list_cn[index+2]
            elif 'none' == rnd_character:
                rnd_character = character_list_cn[index+1]
        else:
            rnd_character = character

        chara = character_dict[rnd_character]                      
        opt_chara = chara.replace('(', '\\(').replace(')', '\\)')                         
                    
        if not math.isclose(character_weight, 1.0):
            opt_chara = '({}:{:0.2f})'.format(opt_chara, character_weight)
            
        if not opt_chara.endswith(','):
            opt_chara = f'{opt_chara},' 
            
        if '' != custom_prompt and not custom_prompt.endswith(','):
            custom_prompt = f'{custom_prompt},'
        
        prompt = f'{opt_chara} {custom_prompt}'
        if insert_before_character:            
            prompt = f'{custom_prompt} {opt_chara}'
        info = f'Character:{rnd_character}[{opt_chara}]\nCustom Promot:{custom_prompt}'
                
        return (prompt, info, )
    
class illustrious_character_select_en:
    '''
    Same as illustrious_character_select
    But list in English tags
    '''                       

    @classmethod
    def INPUT_TYPES(s):
        
        return {
            "optional": {
                "custom_prompt": ("STRING", {
                    "display": "input" ,
                    "multiline": True
                }),                      
            },
            "required": {
                "character": (character_list_en, ),
                "random_action_seed": ("INT", {
                    "default": 1024, 
                    "min": 0, 
                    "max": 0xffffffffffffffff,
                    "display": "input"
                }),
                "character_weight": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 2.0, "step": 0.05}),
                "insert_before_character" : ("BOOLEAN", {"default": False}),
            },
        }
                        
    RETURN_TYPES = ("STRING","STRING",)
    RETURN_NAMES = ("prompt", "info",)
    FUNCTION = "illustrious_character_select_en_ex"
    CATEGORY = cat
    
    def illustrious_character_select_en_ex(self, character, random_action_seed, character_weight, insert_before_character, custom_prompt = ''):
        chara = ''
        rnd_character = ''
        
        if 'random' == character:
            index = random_action_seed % len(character_list_en)
            rnd_character = character_list_en[index]
            if 'random' == rnd_character:
                rnd_character = character_list_en[index+2]
            elif 'none' == rnd_character:
                rnd_character = character_list_en[index+1]
        else:
            rnd_character = character
            
        chara = rnd_character                                                      
        opt_chara = chara.replace('(', '\\(').replace(')', '\\)')          
        
        if not math.isclose(character_weight, 1.0):
            opt_chara = '({}:{:0.2f})'.format(opt_chara, character_weight)

        if not opt_chara.endswith(','):
            opt_chara = f'{opt_chara},'   
            
        if '' != custom_prompt and not custom_prompt.endswith(','):
            custom_prompt = f'{custom_prompt},'
                    
        prompt = f'{opt_chara} {custom_prompt}'
        if insert_before_character:            
            prompt = f'{custom_prompt} {opt_chara}'
        info = f'Character:{rnd_character}[{opt_chara}]\nCustom Promot:{custom_prompt}'
                
        return (prompt, info, )

def download_file(url, file_path):   
    response = requests.get(url)
    response.raise_for_status() 
    print('[{}]:Downloading... {}'.format(cat, url))
    with open(file_path, 'wb') as file:
        file.write(response.content)        

def get_md5_hash(input_str):
    md5_hash = hashlib.md5()
    md5_hash.update(input_str.encode('utf-8'))
    return md5_hash.hexdigest()

def base64_to_image(base64_data):
    compressed_data = base64.b64decode(base64_data)
    webp_data = gzip.decompress(compressed_data)
    image = Image.open(BytesIO(webp_data))  
    return EncodeImage(image)
    
def main():
    global character_list_cn
    global character_list_en
    global character_dict
    global llm_config
        
    # download file
    for item in wai_illustrious_character_select_files:
        name = item['name']
        file_path = item['file_path']
        url = item['url']        
            
        if not os.path.exists(file_path):
            download_file(url, file_path)

        with open(file_path, 'r', encoding='utf-8') as file:
            if 'settings' == name:
                llm_config.update(json.load(file))       
            elif 'wai_character' == name:
                lines = file.readlines()
                for line in lines:
                    key, value = line.split(',')
                    character_dict[key.strip()]=value.strip()
        
        character_list_cn = list(character_dict.keys())    
        character_list_cn.insert(0, "random")
        
        character_list_en = list(character_dict.values())   
        character_list_en.insert(0, "random")
            
#if __name__ == '__main__':
main()
