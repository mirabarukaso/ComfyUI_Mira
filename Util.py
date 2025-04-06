import math
import random
import torch
import numpy as np
from PIL import Image
import cv2
from .color_transfer import ColorTransfer
from comfy_extras.nodes_upscale_model import ImageUpscaleWithModel
import torchvision.transforms as T
import torchvision.transforms.functional as con

class AlwaysEqualProxy(str):
#ComfyUI-Logic 
#refer: https://github.com/theUpsider/ComfyUI-Logic
    def __eq__(self, _):
        return True

    def __ne__(self, _):
        return False

cat = "Mira/Util"
cat_image = "Mira/Util/Image"

def DecodeImage(src_image):
    i = 255. * src_image[0].cpu().numpy()
    img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))    
    return img

def EncodeImage(src_image):
    img = np.array(src_image).astype(np.float32) / 255.0
    img = torch.from_numpy(img)[None,]
    return img

def ConvertToNP(src_image):            
    i = 255. * src_image[0].cpu().numpy()
    array_image = np.clip(i, 0, 255).astype(np.uint8)
    return array_image.astype(np.float32)           

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

def Fixeight(num):
    new_num = int(num)
    if 0 != math.floor(num)%8:
        residue = math.floor(num)%8
        if 3 >= math.floor(num)%8:
            new_num = math.floor(num) - residue
        else:
            new_num = math.floor(num) + 8 - residue    
    return new_num

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
                    "max": 4096,
                    "step": 8,
                    "display": "number" 
                }),
                "Height": ("INT", {
                    "default": 1024,
                    "min": 16,
                    "max": 4096,
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
                    "max": 4096,
                    "step": 8,
                    "display": "number" 
                }),
                "Height": ("INT", {
                    "default": 1024,
                    "min": 16,
                    "max": 4096,
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
    HiResMultiplier - Same as Input
    '''
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "Width": ("INT", {
                    "default": 576,
                    "min": 16,
                    "max": 4096,
                    "step": 8,
                    "display": "number" 
                }),
                "Height": ("INT", {
                    "default": 1024,
                    "min": 16,
                    "max": 4096,
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
                    "min": 0.1,
                    "max": 8,
                    "step": 0.1,
                    "display": "number" 
                }),
            },
        }

    RETURN_TYPES = ("INT","INT","INT","INT","INT","FLOAT")
    RETURN_NAMES = ("Width","Height","Batch","HiRes Width","HiRes Height","HiResMultiplier",)
    FUNCTION = "CanvasCreatorEx"
    CATEGORY = cat
    
    def CanvasCreatorEx(self, Width, Height, Batch, Landscape, HiResMultiplier):              
        Width, Height, Batch, HiResMultiplier = SafeCheck(Width, Height, Batch, HiResMultiplier)
            
        HiResWidth = Fixeight(Width * HiResMultiplier)
        HiResHeight = Fixeight(Height * HiResMultiplier)
                
        if(False == Landscape):            
            intHiResHeight = math.floor(HiResHeight)
            intHiResWidth = math.floor(HiResWidth)
            return(Width, Height, Batch, intHiResWidth, intHiResHeight, HiResMultiplier, )
        else:            
            intHiResHeight = math.floor(HiResHeight)
            intHiResWidth = math.floor(HiResWidth)
            return(Height, Width, Batch, intHiResHeight, intHiResWidth, HiResMultiplier, )
        
        
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

class ImageGrayscale:
    '''
    Convert Image to Grayscale
    
    Inputs:
    src_image           - Source Image
            
    Outputs:
    image               - Torched Image                    
    '''
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "src_image": ("IMAGE", {
                    "default": None, 
                }),          
            },            
        }
        
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "ImageGrayscaleEx"
    CATEGORY = cat_image
    
    def ImageGrayscaleEx(self, src_image):         
        img = DecodeImage(src_image)            
        img_adj = con.to_grayscale(img)                     
        result = EncodeImage(img_adj)
        
        return(result,)    
class ImageContrast:
    '''
    Adjust Image Contrast
    
    Inputs:
    src_image           - Source Image
    level               - Contrast Level, default is 1.0
            
    Outputs:
    image               - Torched Image                    
    '''
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "src_image": ("IMAGE", {
                    "default": None, 
                }),       
                "level": ("FLOAT", {
                    "default": 1.0, 
                    "step": 0.001,
                    "min": 0, 
                    "max": 10
                }),         
            },            
        }
        
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "ImageContrastEx"
    CATEGORY = cat_image
    
    def ImageContrastEx(self, src_image, level):         
        img = DecodeImage(src_image)            
        img_adj = con.adjust_contrast(img, level)                     
        result = EncodeImage(img_adj)
        
        return(result,)
    
class ImageSharpness:
    '''
    Adjust Image Sharpness
    
    Inputs:
    src_image           - Source Image
    level               - Sharpness Level, default is 1.0
            
    Outputs:
    image               - Torched Image                    
    '''
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "src_image": ("IMAGE", {
                    "default": None, 
                }),       
                "level": ("FLOAT", {
                    "default": 1.0, 
                    "step": 0.1,
                    "min": 0, 
                    "max": 100
                }),       
            },            
        }
        
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "ImageSharpnessEx"
    CATEGORY = cat_image
    
    def ImageSharpnessEx(self, src_image, level):         
        img = DecodeImage(src_image)            
        img_adj = con.adjust_sharpness(img, level)                     
        result = EncodeImage(img_adj)
        
        return(result,)
    
class ImageBrightness:
    '''
    Adjust Image Brightness
    
    Inputs:
    src_image           - Source Image
    level               - Brightness Level, default is 1.0
            
    Outputs:
    image               - Torched Image                    
    '''
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "src_image": ("IMAGE", {
                    "default": None, 
                }),       
                "level": ("FLOAT", {
                    "default": 1.0, 
                    "step": 0.001,
                    "min": 0, 
                    "max": 10
                }),         
            },            
        }
        
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "ImageBrightnessEx"
    CATEGORY = cat_image
    
    def ImageBrightnessEx(self, src_image, level):         
        img = DecodeImage(src_image)            
        img_adj = con.adjust_brightness(img, level)                     
        result = EncodeImage(img_adj)
        
        return(result,)
    
class ImageSaturation:
    '''
    Adjust Image Saturation
    
    Inputs:
    src_image           - Source Image
    level               - Saturation Level, default is 0.0
            
    Outputs:
    image               - Torched Image                    
    '''
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "src_image": ("IMAGE", {
                    "default": None, 
                }),       
                "level": ("FLOAT", {
                    "default": 0.0, 
                    "step": 0.001,
                    "min": 0, 
                    "max": 10
                }),         
            },            
        }
        
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "ImageSaturationEx"
    CATEGORY = cat_image
    
    def ImageSaturationEx(self, src_image, level):         
        img = DecodeImage(src_image)            
        img_adj = con.adjust_saturation(img, level)                     
        result = EncodeImage(img_adj)
        
        return(result,)

class ImageHUE:
    '''
    Adjust Image HUE
    
    Inputs:
    src_image           - Source Image
    level               - HUE Level, default is 0.0
            
    Outputs:
    image               - Torched Image                    
    '''
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "src_image": ("IMAGE", {
                    "default": None, 
                }),       
                "level": ("FLOAT", {
                    "default": 0.0, 
                    "step": 0.001,
                    "min": -0.5, 
                    "max": 0.5
                }),         
            },            
        }
        
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "ImageHUEEx"
    CATEGORY = cat_image
    
    def ImageHUEEx(self, src_image, level):         
        img = DecodeImage(src_image)            
        img_adj = con.adjust_hue(img, level)                     
        result = EncodeImage(img_adj)
        
        return(result,)

class ImageGamma:
    '''
    Adjust Image Gamma
    
    Inputs:
    src_image           - Source Image
    level               - Gamma Level, default is 0.0
            
    Outputs:
    image               - Torched Image                    
    '''
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "src_image": ("IMAGE", {
                    "default": None, 
                }),       
                "level": ("FLOAT", {
                    "default": 0.0, 
                    "step": 0.001,
                    "min": 0, 
                    "max": 10
                }),         
            },            
        }
        
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "ImageGammaEx"
    CATEGORY = cat_image
    
    def ImageGammaEx(self, src_image, level):         
        img = DecodeImage(src_image)            
        img_adj = con.adjust_gamma(img, level)                     
        result = EncodeImage(img_adj)
        
        return(result,)
                                                                
class ImageColorTransfer:
    '''
    Refer to: https://en.wikipedia.org/wiki/Image_color_transfer
    
    Image Color Transfer
    
    Inputs:
    src_image           - Source Image
    ref_image           - Reference image. The colors of this Image will applied to the Source Image
            
    Outputs:
    image               - Output Image                    
    '''
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "src_image": ("IMAGE", {
                    "default": None, 
                }),       
                "ref_image": ("IMAGE", {
                    "default": None, 
                }),
                "method" : (['Mean', 'Lab', 'Pdf', 'Pdf+Regrain'], ),
            },            
        }
        
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "ImageColorTransferEx"
    CATEGORY = cat_image
    
    def ImageColorTransferEx(self, src_image, ref_image, method):                               
        PT = ColorTransfer()        
        new_img = None
        if "Mean" == method:
            s = ConvertToNP(src_image)       
            r = ConvertToNP(ref_image)       
            new_img = PT.mean_std_transfer(img_arr_in=s, img_arr_ref=r)
        elif "Lab" == method:
            s = np.array(DecodeImage(src_image), dtype=np.uint8)
            r = np.array(DecodeImage(ref_image), dtype=np.uint8)
            new_img = PT.lab_transfer(img_arr_in=s, img_arr_ref=r)
        elif "Pdf" == method:
            s = ConvertToNP(src_image)       
            r = ConvertToNP(ref_image)       
            new_img = PT.pdf_transfer(img_arr_in=s, img_arr_ref=r, regrain=False)
        else:
            s = ConvertToNP(src_image)       
            r = ConvertToNP(ref_image)       
            new_img = PT.pdf_transfer(img_arr_in=s, img_arr_ref=r, regrain=True) 
            
        result = EncodeImage(new_img)
        
        return(result,)                                           

class ImageToneCurve:
    '''
    Image Tone Curve
    
    Adjust the overall brightness using the `RGB Channels` or `Brightness` node.
    
    Inputs:
    src_image           - Source Image
    low                 - Increase shadow range
    high                - Increase highlight range
            
    Outputs:
    image               - Output Image  
    '''
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "src_image": ("IMAGE", {
                    "default": None, 
                }), 
                "low": ("FLOAT", {
                    "default": -1.0, 
                    "step": 0.01,
                    "min": -10, 
                    "max": 10
                }),       
                "high": ("FLOAT", {
                    "default": 1.0, 
                    "step": 0.01,
                    "min": -10, 
                    "max": 10
                }), 
            },            
        }
        
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "ImageToneCurveEx"
    CATEGORY = cat_image
        
    def ImageToneCurveEx(self, src_image, low, high):       
        y = np.arctan(np.linspace(low, high, 256))
        y = 255 / (y.max() - y.min()) * (y - y.max()) + 255
        
        s = np.array(DecodeImage(src_image), dtype=np.uint8)
        new_img = cv2.LUT(s, y).astype(np.uint8)
        
        result = EncodeImage(new_img)        
        return(result,)  

class ImageRGBChannel:
    '''
    Image RGB Channel
    
    Inputs:
    src_image           - Source Image
    R/G/B               - Colour magnification value, less than 1.0 means attenuation
            
    Outputs:
    image               - Output Image  
    '''
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "src_image": ("IMAGE", {
                    "default": None, 
                }), 
                "Red": ("FLOAT", {
                    "default": 1.0, 
                    "step": 0.01,
                    "min": 0, 
                    "max": 5
                }),       
                "Green": ("FLOAT", {
                    "default": 1.0, 
                    "step": 0.01,
                    "min": 0, 
                    "max": 5
                }),       
                "Blue": ("FLOAT", {
                    "default": 1.0, 
                    "step": 0.01,
                    "min": 0, 
                    "max": 5
                }),     
            },            
        }
        
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "ImageRGBChannelEx"
    CATEGORY = cat_image
    
    def ImageRGBChannelEx(self, src_image, Red, Green, Blue):                       
        s = DecodeImage(src_image)     
        r, g, b = s.split()        
        
        r = r.point(lambda i: i * Red)
        g = g.point(lambda i: i * Green)        
        b = b.point(lambda i: i * Blue)
        
        new_img = Image.merge('RGB', (r, g, b))        
        result = EncodeImage(new_img)        
        return(result,)  
    
class UpscaleImageByModelThenResize:
    '''
    Upscale Image By Model Then Resize
    
    This is an experimental feature for zooming in an image on a model and then zooming out to a specified size (a multiple of 8 in length and width).
    For example, if the input model zooms the image 4x by default and the node is set to zoom 2x, then the image will first be zoomed 4x using the model and then resized to 2x.
    
    Inputs:
    upscale_model       - Model for upscaling
    image               - Source Image
    resize_scale        - Real resize ratio, the result will be the nearest multiple of 8.
    resize_method       - Resize method, nearest, nearest-exact, bilinear, bicubic
            
    Outputs:
    image               - Output Image  
    '''
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": { 
                "upscale_model": ("UPSCALE_MODEL",),
                "image": ("IMAGE", {
                    "default": None, 
                }), 
                "resize_scale": ("FLOAT", {
                    "default": 1.5, 
                    "step": 0.1,
                    "min": 0.1, 
                    "max": 8
                }),  
                "resize_method" : (['nearest', 'nearest-exact', 'bilinear', 'bicubic', 'lanczos'], ),
            },
        }
        
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "UpscaleImageWithModelEx"
    CATEGORY = cat_image

    def UpscaleImageWithModelEx(self, upscale_model, image, resize_scale, resize_method):
        new_img = (ImageUpscaleWithModel.upscale(self, upscale_model, image))[0]
        
        #print('resize_scale: ' + str(resize_scale))
        #print('upscale_model.scale: ' + str(upscale_model.scale))        
        if upscale_model.scale != resize_scale:
            width = image.shape[2]
            height = image.shape[1]
            
            new_width = Fixeight(width*resize_scale)
            new_height = Fixeight(height*resize_scale)        
            #print('new_width: ' + str(new_width))
            #print('new_height: ' + str(new_height))

            interpolation_mode = T.InterpolationMode.NEAREST
            if resize_method == 'nearest-exact':
                interpolation_mode = T.InterpolationMode.NEAREST_EXACT
            elif resize_method == 'bilinear':
                interpolation_mode = T.InterpolationMode.BILINEAR
            elif resize_method == 'bicubic':
                interpolation_mode = T.InterpolationMode.BICUBIC
            elif resize_method == 'lanczos':
                interpolation_mode = T.InterpolationMode.LANCZOS
                
            size = (new_height, new_width)
            transform = T.Resize(size, interpolation=interpolation_mode)
            new_img = transform(DecodeImage(new_img))
                        
            return (EncodeImage(new_img),)
        
        return (new_img,)
    