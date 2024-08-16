import os
import comfy.utils
import folder_paths as comfy_paths

cat = "Mira/Lora"

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
            print('Mira: [ERROR][LoRALoaderWithNameStacker] Load LoRA failed return with original Model and Clip >> ' + lora_name)        
            return (model, clip, lora_stack)

        model_lora, clip_lora = comfy.sd.load_lora_for_models(model, clip, lora, strength_model, strength_clip)
        
        #  LoRA Stracker
        if '' == lora_stack:
            lora_stack = '<lora:' + lora_name + ':' + str(strength_model) + ':' + str(strength_clip) + '>'            
        else:
            if False is (lora_name in lora_stack):
                lora_stack = lora_stack + '<lora:' + lora_name + ':' + str(strength_model) + ':' + str(strength_clip) + '>'
                                
        return (model_lora, clip_lora, lora_stack)
        