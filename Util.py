import math
import random

class AlwaysEqualProxy(str):
#ComfyUI-Logic 
#refer: https://github.com/theUpsider/ComfyUI-Logic
    def __eq__(self, _):
        return True

    def __ne__(self, _):
        return False

cat = "Mira/Util"

def SafeCheck(Width = 16, Height = 16, Batch = 1, HiResMultiplier = 1.0):
        if 16 > Width:
            Width = 16
            
        if 16 > Height:
            Height = 16
            
        if 1 > Batch:
            Batch = 1
            
        if 1.0 > HiResMultiplier:
            HiResMultiplier = 1.0
        
        return Width, Height, Batch, HiResMultiplier

class CanvasCreatorBasic:
    '''
    Create Canvas information Width and Height for Latent.
    
    Inputs:
    Width       - Image Width
    Height      - Image Height
        
    Outputs:
    Width       - Image Width
    Height      - Image Height
    '''
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "Width": ("INT", {
                    "default": 576,
                    "min": 16,
                    "step": 8,
                    "display": "number" 
                }),
                "Height": ("INT", {
                    "default": 1024,
                    "min": 16,
                    "step": 8,
                    "display": "number" 
                }),
            },
        }
                
    RETURN_TYPES = ("INT","INT",)
    RETURN_NAMES = ("Width","Height",)
    FUNCTION = "CanvasCreatorBasicEx"
    CATEGORY = cat
    
    def CanvasCreatorBasicEx(self, Width, Height):                         
        Width, Height, Batch, HiResMultiplier = SafeCheck(Width, Height)
        
        return(Width, Height,)

class CanvasCreatorSimple:
    '''
    Create Canvas information Width and Height for Latent with Landscape switch.
    
    Inputs:
    Width       - Image Width
    Height      - Image Height
    Landscape   - When ENABLED, will swap Width and Height for output
        
    Outputs:
    Width       - Image Width
    Height      - Image Height
    '''
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "Width": ("INT", {
                    "default": 576,
                    "min": 16,
                    "step": 8,
                    "display": "number" 
                }),
                "Height": ("INT", {
                    "default": 1024,
                    "min": 16,
                    "step": 8,
                    "display": "number" 
                }),
                "Landscape": ("BOOLEAN", {
                    "default": False
                }),
            },
        }
                
    RETURN_TYPES = ("INT","INT",)
    RETURN_NAMES = ("Width","Height",)
    FUNCTION = "CanvasCreatorSimpleEx"
    CATEGORY = cat
    
    def CanvasCreatorSimpleEx(self, Width, Height, Landscape):                         
        Width, Height, Batch, HiResMultiplier = SafeCheck(Width, Height)
        
        if(False == Landscape):
            return(Width, Height,)
        else:
            return(Height, Width,)

        
class CanvasCreatorAdvanced:
    '''
    Create Canvas information Width and Height for Latent with Landscape switch, Batch and HiResMultiplier.
    
    Inputs:
    Width           - Image Width
    Height          - Image Height
    Landscape       - When ENABLED, will swap Width and Height for output
    Batch           - Batch size for Latent
    HiResMultiplier - Multiplier setting for high-resolution output 
        
    Outputs:
    Width           - Image Width for Latent
    Height          - Image Height for Latent
    Batch           - Batch size for Latent
    HiRes Width     - Width x HiResMultiplier. The result is not the product of the original data, but the nearest multiple of 8.
    HiRes Height    - Height x HiResMultiplier. 
    Debug           - Debug output
    '''
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "Width": ("INT", {
                    "default": 576,
                    "min": 16,
                    "step": 8,
                    "display": "number" 
                }),
                "Height": ("INT", {
                    "default": 1024,
                    "min": 16,
                    "step": 8,
                    "display": "number" 
                }),
                "Batch": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 16,
                    "step": 1,
                    "display": "number" 
                }),
                "Landscape": ("BOOLEAN", {
                    "default": False
                }),
                "HiResMultiplier": ("FLOAT", {
                    "default": 1.5,
                    "min": 1,
                    "step": 0.1,
                    "display": "number" 
                }),
            },
        }

    RETURN_TYPES = ("INT","INT","INT","INT","INT","STRING",)
    RETURN_NAMES = ("Width","Height","Batch","HiRes Width","HiRes Height","Debug",)
    FUNCTION = "CanvasCreatorEx"
    CATEGORY = cat
    
    def CanvasCreatorEx(self, Width, Height, Batch, Landscape, HiResMultiplier):       
        DebugMessage = 'Mira:'       
        
        Width, Height, Batch, HiResMultiplier = SafeCheck(Width, Height, Batch, HiResMultiplier)
            
        HiResWidth = Width * HiResMultiplier
        HiResHeight = Height * HiResMultiplier        
        
        if 0 != math.floor(HiResWidth)%8:
            DebugMessage += '\n(Before)HiResWidth = ' + str(math.floor(HiResWidth))
            residue = math.floor(HiResWidth)%8
            if 3 >= math.floor(HiResWidth)%8:
                HiResWidth = math.floor(HiResWidth) - residue
            else:
                HiResWidth = math.floor(HiResWidth) + 8 - residue
            DebugMessage += '\n(After)HiResWidth = ' + str(math.floor(HiResWidth))            
            
        if 0 != math.floor(HiResHeight)%8:
            DebugMessage += '\n(Before)HiResHeight = ' + str(math.floor(HiResHeight))
            residue = math.floor(HiResHeight)%8
            if 3 >= math.floor(HiResHeight)%8:
                HiResHeight = math.floor(HiResHeight) - residue
            else:
                HiResHeight = math.floor(HiResHeight) + 8 - residue
            DebugMessage += '\n(After)HiResHeight = ' + str(math.floor(HiResHeight))
        
        if(False == Landscape):
            DebugMessage += '\nWidth = ' + str(Width)
            DebugMessage += '\nHeight = ' + str(Height)
            DebugMessage += '\nHiResWidth = ' + str(math.floor(HiResWidth))
            DebugMessage += '\nHiResHeight = ' + str(math.floor(HiResHeight))
            
            intHiResHeight = math.floor(HiResHeight)
            intHiResWidth = math.floor(HiResWidth)
            return(Width, Height, Batch, intHiResWidth, intHiResHeight, DebugMessage,)
        else:
            DebugMessage += '\nLandscape actived, swap Height and Width'
            DebugMessage += '\nWidth = ' + str(Height)
            DebugMessage += '\nHeight = ' + str(Width)
            DebugMessage += '\nHiResWidth = ' + str(math.floor(HiResWidth))
            DebugMessage += '\nHiResHeight = ' + str(math.floor(HiResHeight))
            
            intHiResHeight = math.floor(HiResHeight)
            intHiResWidth = math.floor(HiResWidth)
            return(Height, Width, Batch, intHiResHeight, intHiResWidth, DebugMessage,)
        
        
class RandomTillingLayouts:
    '''
    [#1](https://github.com/mirabarukaso/ComfyUI_Mira/issues/1)   
    
    Random Tilling Mask Layout Generator   
    Highly recommend connect the output `layout` or `Create Tilling PNG Mask -> Debug` to `ShowText` node.   
    
    **Known Issue** about `Seed Generator`   
    Switching `randomize` to `fixed` now works immediately.   
    But, switching `fixed` to `randomize`, it need 2 times `Queue Prompt` to take affect. (Because of the ComfyUI logic)   
      
    Solution: Try `Global Seed (Inspire)` from [ComfyUI-Inspire-Pack](https://github.com/ltdrdata/ComfyUI-Inspire-Pack)

    **Reminder **   
    The `rnd_seed` have nothing to do with the actual random numbers,   
    you can't get the same `layout` with the same `rnd_seed`,   
    it is recommended to use `ShowText` and `Notes` to save your favourite `layout`.   

    **Hint**   
    Set rows or colums to `0` for only one direction cuts.   
    Whichever is set to `0` will automatically cut according to the other non-zero setting.   
    Just in case all fours are `0`, it will return `1,1`.   
    
    Inputs:
    min_rows, max_rows      - Range of how many `N cuts` you may want, set both to 0 to disable it.
    min_colums, max_colums  - Range of how many `G cuts` you may want, set both to 0 to disable it.       
    max_weights_gcuts       - The maxium weight of `G cuts` range from 1 to `max_weights_gcuts`
    max_weights_ncuts       - The maxium weight of `N cuts` range from 1 to `max_weights_ncuts`
    
    rnd_seed                - Connect to the `Seed Generator` node, then use `Global Seed (Inspire)` node to control it properly.
            
    Outputs:
    Layout                  - Layouts string, you need connect it to `Create Tilling PNG Mask -> layout`
    
    Example:
    [2,2,2,1]@3.8,4.2,2.1,3.3;3.6,3.5,3.3,3.7;2.7,3.2,4.9
     ^ * * *
    ^2 colums
        * the 1st block has 2 rows (3 blocks)
        * the 2nd block has 2 rows (3 blocks)
        * the 3rd block has 1 row (2 blocks)
    3+3+2= 8 blocks in total        
    
    Colum_first == False                 
    1|4|7
    2|5|
    3|6|8
    
    '''
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "min_rows": ("INT", {
                    "default": 1,
                    "min": 0,
                    "max": 16,
                    "step": 1,
                    "display": "number" 
                }),
                "max_rows": ("INT", {
                    "default": 1,
                    "min": 0,
                    "max": 16,
                    "step": 1,
                    "display": "number" 
                }),
                "min_colums": ("INT", {
                    "default": 1,
                    "min": 0,
                    "max": 16,
                    "step": 1,
                    "display": "number" 
                }),
                "max_colums": ("INT", {
                    "default": 1,
                    "min": 0,
                    "max": 16,
                    "step": 1,
                    "display": "number" 
                }),
                "max_weights_gcuts": ("FLOAT", {
                    "default": 2.0,
                    "min": 1.0,
                    "max": 10.0,
                    "step": 0.1,
                    "display": "number" 
                }),
                "max_weights_ncuts": ("FLOAT", {
                    "default": 2.0,
                    "min": 1.0,
                    "max": 10.0,
                    "step": 0.1,
                    "display": "number" 
                }),
                "rnd_seed": (AlwaysEqualProxy('*'), {
                    "default": 0, 
                    "min": 0, 
                    "max": 0xffffffffffffffff,
                    "display": "input" 
                }),
            },            
        }
        
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("layout",)
    FUNCTION = "RandomTillingLayoutsEx"
    CATEGORY = cat
    
    def RandomTillingLayoutsEx(self, min_rows, max_rows, min_colums, max_colums, max_weights_gcuts, max_weights_ncuts, rnd_seed):
        if min_colums > max_colums:
            min_colums = max_colums
        
        if min_rows > max_rows:
            min_rows = max_rows
            
        if 0 == max_colums and max_colums == max_rows:
            layouts = "1,1"
            return (layouts,)
        
        if 0 == max_colums or 0 == max_rows:
            max_colums = max(max_colums, max_rows)
        
        colums = random.randrange(min_colums, max_colums + 1)        
        #print("Mira: colums: " + str(colums))
    
        row_and_colum_info = '[' + str(rnd_seed) + '][' + str(colums) + ","
        layouts = ""    
        if 0 == colums:
            rows = random.randrange(min_rows, max_rows + 1)
            #print("Mira: colums = 0 rows: " + str(rows))
            if 0 == rows:
                row_and_colum_info += "0,"
                layouts = "1,1"
            else:
                row_and_colum_info += str(rows) + ","
                for _ in range(0, rows + 1):
                    layouts += str(round(random.uniform(1, max_weights_ncuts),1))
                    layouts += ","
                layouts = layouts[:-1]   
        else:        
            for _ in range(0, colums + 1):
                layouts += str(round(random.uniform(1, max_weights_gcuts),1))
                rows = random.randrange(min_rows, max_rows + 1)
                #print("Mira: rows: " + str(rows))
                if 0 == rows:
                    row_and_colum_info += "0,"
                    layouts += ",1"
                else:
                    row_and_colum_info += str(rows) + ","
                    layouts += ","
                    for _ in range(0, rows + 1):
                        layouts += str(round(random.uniform(1, max_weights_ncuts),1))
                        layouts += ","
                    layouts = layouts[:-1]            
                layouts += ";"
            layouts = layouts[:-1]    
            
        row_and_colum_info = row_and_colum_info[:-1]            
        row_and_colum_info += ']@'
                    
        return (row_and_colum_info + layouts,)

class RandomNestedLayouts:
    '''   
    Random Nested Mask Layout Generator   
    All known issues same as upper one.
    
    Inputs:
    min_nested, max_nested      - Range of nest you want.
    min_weights, max_weights    - The weight of every nest.
    rnd_seed                    - Connect to the `Seed Generator` node, then use `Global Seed (Inspire)` node to control it properly.
            
    Outputs:
    Layout                      - Layouts string, you need connect it to `Create Nested PNG Mask -> layout`
    top, bottom, left, right    - Random Boolean
    '''
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "min_nested": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 32,
                    "step": 1,
                    "display": "number" 
                }),
                "max_nested": ("INT", {
                    "default": 2,
                    "min": 1,
                    "max": 32,
                    "step": 1,
                    "display": "number" 
                }),
                "min_weights": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.1,
                    "max": 10.0,
                    "step": 0.1,
                    "display": "number" 
                }),
                "max_weights": ("FLOAT", {
                    "default": 2.0,
                    "min": 1.0,
                    "max": 10.0,
                    "step": 0.1,
                    "display": "number" 
                }),
                "rnd_seed": (AlwaysEqualProxy('*'), {
                    "default": 0, 
                    "min": 0, 
                    "max": 0xffffffffffffffff,
                    "display": "input" 
                }),
            },            
        }
        
    RETURN_TYPES = ("STRING", "BOOLEAN", "BOOLEAN", "BOOLEAN", "BOOLEAN")
    RETURN_NAMES = ("layout", "top", "bottom", "left", "right")
    FUNCTION = "RandomNestedLayoutsEx"
    CATEGORY = cat
    
    def RandomNestedLayoutsEx(self, min_nested, max_nested, min_weights, max_weights, rnd_seed):
        if min_nested > max_nested:
            min_nested = max_nested        
        
        if min_weights > max_weights:
            min_weights = max_weights
            
        nested = random.randrange(min_nested, max_nested + 1)        
    
        bool1 = bool(random.getrandbits(1))
        bool2 = bool(random.getrandbits(1))
        bool3 = bool(random.getrandbits(1))
        bool4 = bool(random.getrandbits(1))
    
        generator_info = '[' + str(rnd_seed) + '][' + str(nested) + '][' + str(bool1) + ',' + str(bool2) + ',' + str(bool3) + ',' + str(bool4) + ']@'
        layouts = ""  
        
        for _ in range(0, nested):
            layouts += str(round(random.uniform(min_weights, max_weights),1))
            layouts += ','
            
        layouts = layouts[:-1]
                
        return (generator_info + layouts, bool1, bool2, bool3, bool4,)
        
class SeedGenerator:
    '''
    SeedGenerator
    '''
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "seed": ("INT", {
                    "default": 0, 
                    "min": 0, 
                    "max": 0xffffffffffffffff
                }),
            },            
        }
        
    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("seed",)
    FUNCTION = "SeedGeneratorEx"
    CATEGORY = cat
    
    def SeedGeneratorEx(self, seed):
        return(seed,)
    
    