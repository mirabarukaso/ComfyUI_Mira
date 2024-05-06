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
    
        random.seed(rnd_seed)
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
    
        random.seed(rnd_seed)
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
    
class CirclesGenerator:
    '''
    ***Used to thought that would be fun, but it doesn't works well, let me know if you create something fun with it***
    
    `Circles Generator` connect to `Create Circle Mask`
    Generate a circle with random position, if you need to generate it at the specified position, please connect the `optional Circle Creator`, after connecting it will bypass the setting information within this node.
    
    Inputs:
    X, Y, Width, Height         - Zone where you want create circles, set to `0, 0, C_W, C_H` for whole canvas
    counts                      - How many circles?
    diameter_min, diameter_max  - The `min` and `max` diameter size.
    dount, dount_size           - Enable to create `dount circle`, `dount_size` controls the precent of inner circle diameter.
    overlap                     - When `Disable`, node will check each circle carefuly to ensure there's no `overlap` on each other.   
                                  ***Warning: If you put too much circle on a small zone and `Disable` overlap, it may take a few minutes (depends on retire times) and still has overlap circles.***
    overlap_retry               - Define how may retry times when overlaped. 
    
    rnd_seed                    - Connect to the `Seed Generator` node, then use `Global Seed (Inspire)` node to control it properly.
                
    Outputs:
    circle_list                 - A list of all randomized circles information, connect it to `Create Circle Mask -> circle_provider`
    Width, Height               - AS IS, may need for `Create Circle Mask` 
    '''        
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "X": ("INT", {
                    "default": 0,
                    "min": 0,
                    "step": 1,
                    "display": "number" 
                }),
                "Y": ("INT", {
                    "default": 0,
                    "min": 0,
                    "step": 1,
                    "display": "number" 
                }),                  
                "Width": ("INT", {
                    "default": 576,
                    "min": 0,
                    "step": 1,
                    "display": "number" 
                }),
                "Height": ("INT", {
                    "default": 1024,
                    "min": 0,
                    "step": 1,
                    "display": "number" 
                }),    
                
                "counts": ("INT", {
                    "default": 1, 
                    "min": 1, 
                    "max": 256,
                }),                
                "diameter_min": ("INT", {
                    "default": 32, 
                    "min": 1, 
                    "max": 512,
                }), 
                "diameter_max": ("INT", {
                    "default": 32, 
                    "min": 1, 
                    "max": 512,
                }),                        
                "dount": ("BOOLEAN", {"default": False}),
                "dount_size": ("FLOAT", {
                    "default": 0.5, 
                    "min": 0.1, 
                    "max": 1.0,
                    "step": 0.1,
                }),
                
                "overlap": ("BOOLEAN", {"default": True}),
                "overlap_retry": ("INT", {
                    "default": 128,
                    "min": 1,
                    "max": 4096,
                    "step": 32,
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
        
    RETURN_TYPES = ("CIRCLES_LIST", "INT", "INT",)
    RETURN_NAMES = ("circles_provider", "Width", "Height", )
    FUNCTION = "CirclesRandomGeneratorEx"
    CATEGORY = cat
        
    def CirclesRandomGeneratorEx(self, X, Y, Width, Height, counts, diameter_min, diameter_max, dount, dount_size, overlap, overlap_retry, rnd_seed):
        def CheckOverlap(circle_list, overlap, overlap_retry, X, Y, Width, Height):
            retry = not overlap
            r_times = 0
            
            c_X = random.randrange(X, Width)
            c_Y = random.randrange(Y, Height)
                    
            while True is retry:
                retry = False
                r_times += 1
                if r_times == overlap_retry:
                    #print('Mira: retry failed')
                    break
                
                for circle in circle_list:
                    e_X = circle[0]
                    e_Y = circle[1]
                    dim = circle[2]
                    
                    if e_X <= c_X <= (e_X + dim):
                        retry = True
                        if e_X + dim >= Width:
                            c_X = random.randrange(X, e_X + dim)
                            c_Y = random.randrange(Y, Height)
                        else:
                            c_X = random.randrange(e_X + dim, Width)
                            c_Y = random.randrange(Y, Height)
                        break
                    
                    if e_Y <= c_Y <= (e_Y + dim):
                        retry = True
                        if e_Y + dim >= Height:
                            c_Y = random.randrange(Y, e_Y + dim)
                            c_X = random.randrange(X, Width)
                        else:
                            c_Y = random.randrange(e_Y + dim, Height)
                            c_X = random.randrange(X, Width)
                        break
                    
            return c_X, c_Y
    
        circle_list = []               
        if diameter_min > diameter_max:
            diameter_min = diameter_max
            
        if X >= Width:
            X = 0
        
        if Y >= Height:
            Y = 0
            
        random.seed(rnd_seed)
        for _ in range(counts):                                
            if diameter_min == diameter_max:
                diameter = diameter_min
            else:
                diameter = random.randrange(diameter_min, diameter_max)
                
            c_X, c_Y = CheckOverlap(circle_list, overlap, overlap_retry, X, Y, Width - diameter, Height - diameter)
                
            is_dount = dount
            is_dount_size = dount_size
            
            circle = (c_X, c_Y, diameter, is_dount, is_dount_size)
            #print('Draw ' + str(circle) + ' len = ' + str(len(circle)) + '\n')
            circle_list.append(circle)
            
        return(circle_list, Width, Height,)

class CircleCreator:
    '''
    ***Used to thought that would be fun, but it doesn't works well, let me know if you create something fun with it***
    
    `Circle Creator` connect to `Create Circle Mask`    
    Create a custom circle.
    
    Inputs:
    c_X, c_Y                - ***NOTE:*** This is the `Top Left` position of your circle, not the center.
    diameter            - Diameter of the circle.
    dount, dount_size   - Enable to create `dount circle`, `dount_size` controls the precent of inner circle diameter.
            
    Outputs:
    opt_circle          - An override node, connect to `Create Circle Mask->opt_circle`
    '''
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "c_X": ("INT", {
                    "default": 256,
                    "min": 0,
                    "step": 1,
                    "display": "number" 
                }),
                "c_Y": ("INT", {
                    "default": 256,
                    "min": 0,
                    "step": 1,
                    "display": "number" 
                }),                                                  
                "diameter": ("INT", {
                    "default": 128, 
                    "min": 1, 
                    "max": 4096,
                }),                       
                "dount": ("BOOLEAN", {"default": False}),                
                "dount_size": ("FLOAT", {
                    "default": 0.5, 
                    "min": 0.1, 
                    "max": 1.0,
                    "step": 0.1,
                }),
            },            
        }
        
    RETURN_TYPES = ("CIRCLE_LIST", )
    RETURN_NAMES = ("opt_circle", )
    FUNCTION = "CircleCreatorEx"
    CATEGORY = cat
    
    def CircleCreatorEx(self, c_X, c_Y, diameter, dount, dount_size):        
        circle_list = []
        circle = (c_X, c_Y, diameter, dount, dount_size)
        circle_list.append(circle)        
        return (circle_list, )
    
    