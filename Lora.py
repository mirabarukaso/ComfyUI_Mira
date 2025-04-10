import os
import re
import comfy.utils
import folder_paths as comfy_paths

cat = "Mira/Lora"

def extract_bracket_content(input_text: str) -> list:
    pattern = r'<lora:[^>]*>'
    return re.findall(pattern, input_text)

def parse_content(content: str) -> list:
    inner_content = content[1:-1]  
    if not inner_content.startswith('lora:') or inner_content == 'lora:':
        return None
        
    parts = inner_content[5:].split(':') 
    name = parts[0]
    if not name:
        return None
    
    values = [1.0, 1.0, 1.0, 1.0]
    try:
        if len(parts) > 1:
            param_count = len(parts) - 1
            float_vals = [float(val) for val in parts[1:]]
            if param_count == 2:
                values = [float_vals[0], float_vals[1], float_vals[0], float_vals[1]]
            elif param_count >= 1:
                for i, val in enumerate(float_vals[:4]):
                    values[i] = val
        return [name] + values
    except ValueError:
        return None

def remove_brackets(input_text: str) -> str:
    pattern = r'<lora:[^>]*>'
    return re.sub(pattern, '', input_text).strip()

def process_text(input_text: str) -> tuple[list, str]:
    bracket_contents = extract_bracket_content(input_text)
    
    lora_result = []
    for content in bracket_contents:
        parsed = parse_content(content)
        if parsed is not None:
            lora_result.append(parsed)
            
    plain_text = remove_brackets(input_text)    
    return lora_result, plain_text

class LoRALoaderWithNameStacker:
    '''
    Load LoRA with optional LoRA Name Stacker input/output and bypass trigger
    
    Few Code refer to WAS_Node_Suite
    https://github.com/WASasquatch/was-node-suite-comfyui/blob/ee2e31a1e5fd85ad6f5c36831ffda6fea8f249c7/WAS_Node_Suite.py#L13709
    
    Inputs:
    model               - Your Model node, the purple one.
    clip                - your Clip node, the lemon yellow one.
    lora_name           - Selected LoRA
    strength_model      - LoRA strength for Model
    strength_clip       - LoRA strength for Clip
    bypass              - Bypass current LoRA
    
    Optional Input:
    lora_stack          - A string array from previous `LoRA Loader With Name Stacker`
        
    Outputs:
    MODEL               - Combined text output   
    CLIP                - Alternative combined text output    
    lora_stack          - New string array with current LoRA name and strength information. AS is when bypass is `Enable` or strengths are all `0`
    '''
    
    # Cache
    def __init__(self):
        self.loaded_lora = None;
        
    @classmethod
    def INPUT_TYPES(s):
        lora_list = comfy_paths.get_filename_list("loras")
        if 0 == len(lora_list):
            lora_list.insert(0, "None")
        
        return {
            "optional": {
                "lora_stack": ("STRING", {
                    "display": "input" 
                }),      
            },
            "required": {
                "model": ("MODEL",),
                "clip": ("CLIP", ),
                "lora_name": (lora_list, ),
                "strength_model": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                "strength_clip": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),           
                "bypass": ("BOOLEAN", {"default": False}),  
            },
        }
        
    RETURN_TYPES = ("MODEL", "CLIP", "STRING")
    RETURN_NAMES = ("MODEL", "CLIP", "lora_stack")
    FUNCTION = "LoRALoaderWithNameStackerEx"
    CATEGORY = cat
    
    def LoRALoaderWithNameStackerEx(self, model, clip, lora_name, strength_model, strength_clip, bypass, lora_stack = ''):
        if True is bypass or "None" == lora_name:
            return (model, clip, lora_stack)
        
        if 0 == strength_model and 0 == strength_clip:
            return (model, clip, lora_stack)
        
        lora_path = comfy_paths.get_full_path("loras", lora_name)
        lora = None
        # Check cached or new LoRA
        if self.loaded_lora is not None:
            if self.loaded_lora[0] == lora_path:
                lora = self.loaded_lora[1]
            else:
                temp = self.loaded_lora
                self.loaded_lora = None
                del temp

        if lora is None:            
            lora = comfy.utils.load_torch_file(lora_path, safe_load=True)
            self.loaded_lora = (lora_path, lora)
        
        if lora is None:
            print(f'Mira: [ERROR][LoRALoaderWithNameStacker] Load LoRA failed return with original Model and Clip >> {lora_name}')        
            return (model, clip, lora_stack)

        model_lora, clip_lora = comfy.sd.load_lora_for_models(model, clip, lora, strength_model, strength_clip)
        
        #  LoRA Stracker
        if '' == lora_stack:
            lora_stack = '<lora:' + lora_name + ':' + str(strength_model) + ':' + str(strength_clip) + '>'            
        else:
            if False is (lora_name in lora_stack):
                lora_stack = lora_stack + '<lora:' + lora_name + ':' + str(strength_model) + ':' + str(strength_clip) + '>'
                                
        return (model_lora, clip_lora, lora_stack,)
        
class LoRAfromText:
    '''
    LoRA from Text
    
    <loraname>
    <loraname:model str>
    <loraname:model str:clip str>
    <loraname:model str:clip str:hires model str:hires clip str>
    
    Inputs:
    model               - From your Model node.
    clip                - From your Clip node.
    text                - Text prompt with lora and trigger words
            
    Outputs:
    model               - Connect to 1st sampler MODEL
    clip                - Connect to yout positive CLIP Text Encoder
    model_to_hifix      - Connect to 2nd sampler MODEL, e.g. Hi-res Fix
    clip_to_hifix       - In case you need change prompts in 2nd stage
    plain_text          - Connect to your positive CLIP Text Encoder or text combiner
    '''
    
    @classmethod
    def INPUT_TYPES(s):        
        return {
            "required": {
                "model": ("MODEL",),
                "clip": ("CLIP", ),
                "text": ("STRING", {
                    "multiline": True, 
                }),
            },
        }
        
    RETURN_TYPES = ("MODEL", "CLIP", "MODEL", "CLIP", "STRING")
    RETURN_NAMES = ("model", "clip", "model_to_hifix", "clip_to_hifix", "plain_text")
    FUNCTION = "LoRAfromTextEx"
    CATEGORY = cat
    
    def LoRAfromTextEx(self, model, clip, text):                        
        lora_list, plain_text = process_text(text)
        #print(f'Mira: [LoRALoaderWithNameStacker] lora_list >> {lora_list}')
        #print(f'Mira: [LoRALoaderWithNameStacker] plain_text >> {plain_text}')
        
        model_1 = model
        clip_1 = clip        
        model_2 = model
        clip_2 = clip
        for lora_data in lora_list:                
            lora_name, s1, c1, s2, c2 = lora_data[0], lora_data[1], lora_data[2], lora_data[3], lora_data[4]
            #print(f'Mira: [LoRALoaderWithNameStacker] lora_data >> {lora_name} {s1} {c1} {s2} {c2}')
            
            lora_path = comfy_paths.get_full_path("loras", lora_name)
            if lora_path is None:
                print(f'Mira: [ERROR][LoRALoaderWithNameStacker] Load LoRA failed lora_path >> {lora_path}')        
            else:
                lora = comfy.utils.load_torch_file(lora_path, safe_load=True)
                if 0!=s1 or 0!=c1:
                    model_1, clip_1 = comfy.sd.load_lora_for_models(model_1, clip_1, lora, s1, c1)
                    
                if 0!=s2 or 0!=c2:
                    model_2, clip_2 = comfy.sd.load_lora_for_models(model_2, clip_2, lora, s2, c2)
        
        return (model_1, clip_1, model_2, clip_2, plain_text)
    
    