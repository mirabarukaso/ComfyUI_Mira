import math
import random
import torch
import numpy as np
from PIL import Image
import cv2
from .color_flat import flat_color_multi_scale
from .color_transfer import ColorTransfer
#from comfy_extras.nodes_upscale_model import ImageUpscaleWithModel
from comfy import model_management
import torchvision.transforms as T
import torchvision.transforms.functional as con
import folder_paths
import comfy.utils
import base64
import gzip
from io import BytesIO

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

def decompress_base64_gzip(base64_string):
    try:
        gzipped_data = base64.b64decode(base64_string)
        decompressed_data = gzip.decompress(gzipped_data)
        return bytearray(decompressed_data)
        
    except Exception as error:
        print(f'[decompress_base64_gzip]: Error on decompressing: {error}')
        return None
    
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
        if not isinstance(src_image, torch.Tensor):
            raise ValueError("src_image must be a torch.Tensor")
        if not isinstance(ref_image, torch.Tensor):
            raise ValueError("ref_image must be a torch.Tensor")

        if src_image.ndim == 3:
            src_image = src_image.unsqueeze(0)
        if ref_image.ndim == 3:
            ref_image = ref_image.unsqueeze(0)

        batch_size = src_image.shape[0]
        ref_batch_size = ref_image.shape[0]

        # Ensure ref_image batch size is either 1 or equal to src_image batch size
        if ref_batch_size == 1:
            ref_images = [ref_image[0]] * batch_size
        elif ref_batch_size == batch_size:
            ref_images = [ref_image[i] for i in range(batch_size)]
        else:
            raise ValueError("ref_image batch size must be 1 or equal to src_image batch size")

        PT = ColorTransfer()
        out_imgs = []
        for i in range(batch_size):
            s = src_image[i].unsqueeze(0)
            r = ref_images[i].unsqueeze(0)
            if method == "Mean":
                s_np = ConvertToNP(s)
                r_np = ConvertToNP(r)
                new_img = PT.mean_std_transfer(img_arr_in=s_np, img_arr_ref=r_np)
            elif method == "Lab":
                s_pil = np.array(DecodeImage(s), dtype=np.uint8)
                r_pil = np.array(DecodeImage(r), dtype=np.uint8)
                new_img = PT.lab_transfer(img_arr_in=s_pil, img_arr_ref=r_pil)
            elif method == "Pdf":
                s_np = ConvertToNP(s)
                r_np = ConvertToNP(r)
                new_img = PT.pdf_transfer(img_arr_in=s_np, img_arr_ref=r_np, regrain=False)
            else:
                s_np = ConvertToNP(s)
                r_np = ConvertToNP(r)
                new_img = PT.pdf_transfer(img_arr_in=s_np, img_arr_ref=r_np, regrain=True)
            result = EncodeImage(new_img)
            out_imgs.append(result)

        out_imgs_tensor = torch.cat(out_imgs, dim=0)
        if out_imgs_tensor.ndim == 3:
            out_imgs_tensor = out_imgs_tensor.unsqueeze(0)
        return (out_imgs_tensor,)                                       

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
                "resize_method" : (['lanczos', 'nearest', 'nearest-exact', 'bilinear', 'bicubic', 'box', 'hamming'], ),
            },
        }
        
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "UpscaleImageWithModelEx"
    CATEGORY = cat_image

    def UpscaleImageWithModelEx(self, upscale_model, image, resize_scale, resize_method):         
        def resize_torch_image(img, size, interpolation_mode):
            transform = T.Resize(size, interpolation=interpolation_mode, antialias=True)
            resized_img = transform(DecodeImage(img))
            result = EncodeImage(resized_img)  # [1, C, H, W]
            return result
        
        # refer: https://github.com/comfyanonymous/ComfyUI/blob/4ffea0e864275301329ddb5ecc3fbc7211d7a802/comfy_extras/nodes_upscale_model.py#L50
        def upscale(upscale_model, image):
            device = model_management.get_torch_device()

            memory_required = model_management.module_size(upscale_model.model)
            memory_required += (512 * 512 * 3) * image.element_size() * max(upscale_model.scale, 1.0) * 384.0 #The 384.0 is an estimate of how much some of these models take, TODO: make it more accurate
            memory_required += image.nelement() * image.element_size()
            model_management.free_memory(memory_required, device)
            upscale_model.to(device)
            in_img = image.movedim(-1,-3).to(device)
            tile = 512
            overlap = 32
            oom = True
            while oom:
                try:
                    steps = in_img.shape[0] * comfy.utils.get_tiled_scale_steps(in_img.shape[3], in_img.shape[2], tile_x=tile, tile_y=tile, overlap=overlap)
                    pbar = comfy.utils.ProgressBar(steps)
                    s = comfy.utils.tiled_scale(in_img, lambda a: upscale_model(a), tile_x=tile, tile_y=tile, overlap=overlap, upscale_amount=upscale_model.scale, pbar=pbar)
                    oom = False
                except model_management.OOM_EXCEPTION as e:
                    tile //= 2
                    if tile < 128:
                        raise e

            upscale_model.to("cpu")
            s = torch.clamp(s.movedim(-3,-1), min=0, max=1.0)
            return (s,)
                   
        interpolation_mode = T.InterpolationMode.NEAREST
        if resize_method == 'nearest-exact':
            interpolation_mode = T.InterpolationMode.NEAREST_EXACT
        elif resize_method == 'bilinear':
            interpolation_mode = T.InterpolationMode.BILINEAR
        elif resize_method == 'bicubic':
            interpolation_mode = T.InterpolationMode.BICUBIC
        elif resize_method == 'lanczos':
            interpolation_mode = T.InterpolationMode.LANCZOS
        elif resize_method == 'box':
            interpolation_mode = T.InterpolationMode.BOX
        elif resize_method == 'hamming':    
            interpolation_mode = T.InterpolationMode.HAMMING
    
        if image.shape[3] == 3:  # [B, H, W, C]
            width = image.shape[2]
            height = image.shape[1]
        else:   # [B, C, H, W]
            width = image.shape[3]
            height = image.shape[2]            
            
        new_width = Fixeight(width*resize_scale)
        new_height = Fixeight(height*resize_scale)        
        size = (new_height, new_width)        
            
        new_img = (upscale(upscale_model, image))[0]
        batch_size = new_img.shape[0]
        
        out_imgs = []
        if batch_size == 1:
            result = resize_torch_image(new_img, size, interpolation_mode)  # [1, C, H, W]
            out_imgs.append(result)
        else:
            for i in range(batch_size):
                img_i = new_img[i]  # [H, W, C]
                result = resize_torch_image(img_i.unsqueeze(0), size, interpolation_mode)  # [1, C, H, W]
                out_imgs.append(result)           

        out_imgs_tensor = torch.cat(out_imgs, dim=0)  # [B, C, H, W]
        if out_imgs_tensor.ndim == 3:
            out_imgs_tensor = out_imgs_tensor.unsqueeze(0)
                                            
        return (out_imgs_tensor,)
    
class CheckpointLoaderSimple:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "ckpt_name": (folder_paths.get_filename_list("checkpoints"), {"tooltip": "The name of the checkpoint (model) to load."}),
            }
        }
    RETURN_TYPES = ("MODEL", "CLIP", "VAE", "STRING")
    RETURN_NAMES = ("MODEL", "CLIP", "VAE", "model_name")
    OUTPUT_TOOLTIPS = ("The model used for denoising latents.",
                       "The CLIP model used for encoding text prompts.",
                       "The VAE model used for encoding and decoding images to and from latent space.",
                       "The model_name used for Image Save node to save model name.")
    FUNCTION = "load_checkpoint_ex"

    CATEGORY = cat
    DESCRIPTION = "Loads a diffusion model checkpoint, diffusion models are used to denoise latents."

    def load_checkpoint_ex(self, ckpt_name):
        ckpt_path = folder_paths.get_full_path_or_raise("checkpoints", ckpt_name)
        out = comfy.sd.load_checkpoint_guess_config(ckpt_path, output_vae=True, output_clip=True, embedding_directory=folder_paths.get_folder_paths("embeddings"))
        final_out = (*out[:3], ckpt_name)
        return final_out

class GzippedBase64ToImage:    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {                
                "base64text":  ("STRING", {"display": "input", "multiline": True}),
            }
        }
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    OUTPUT_TOOLTIPS = ("Load Gzipped Base64 Image string from SAA.",
                       "Convert back to Image for other nodes.")
    FUNCTION = "GzippedBase64ToImageEx"

    CATEGORY = cat_image
    DESCRIPTION = "Load Gzipped Base64 Image string from SAA. Convert back to Image for other nodes."

    def GzippedBase64ToImageEx(self, base64text):
        result = decompress_base64_gzip(base64text)        
        img = Image.open(BytesIO(result))
        img.load()
        if img.mode == "RGBA":            
            new_img = Image.new("RGB", img.size, (255,255,255))
            new_img.paste(img, mask=img.split()[3])
            image = EncodeImage(new_img)        
        else:
            image = EncodeImage(img)
        
        return (image,)

class ImageToGzippedBase64:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE", {
                    "default": None, 
                }), 
            }
        }
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("base64text",)
    OUTPUT_TOOLTIPS = ("Load Image and Gzipped then convert to Base64 string for SAA.")
    FUNCTION = "ImageToGzippedBase64Ex"

    CATEGORY = cat_image
    DESCRIPTION = "Load Image and Gzipped then convert to Base64 string for SAA."

    def ImageToGzippedBase64Ex(self, image):
        image_pil = DecodeImage(image)
        temp = BytesIO()
        image_pil.save(temp, format="png")
        compressed_data = gzip.compress(temp.getvalue())        
        img_str_base64 = base64.b64encode(compressed_data).decode("ascii")
        
        return (img_str_base64,)
    
import torch

class ReverseImageAndAllImages:
    '''
    Reverse the order of images in a batch and concatenate the reversed images with the original batch.
    
    Inputs:
    images              - Source Images
            
    Outputs:
    rev_image           - Reversed Images
    all_image           - Source + Reversed Images
    '''
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE", {
                    "default": None, 
                }), 
            },            
        }
        
    RETURN_TYPES = ("IMAGE", "IMAGE", )
    RETURN_NAMES = ("rev_image", "all_image", )
    FUNCTION = "ReverseImageAndAllImagesEx"
    CATEGORY = cat_image
    
    def ReverseImageAndAllImagesEx(self, images):
        # Ensure images is a torch tensor
        if not isinstance(images, torch.Tensor):
            raise ValueError("Input 'images' must be a torch.Tensor")
        
        # The input 'images' is a batched tensor of shape (B, H, W, C), where B is the batch size (number of images).
        effective_count = images.shape[0]
        
        # Extract the first 'effective_count' images to reverse
        to_reverse = images[:effective_count]
        
        # Reverse the order along the batch dimension
        rev_image = to_reverse.flip(0)  # Using flip(0) for batch dimension reversal
        
        # Append the reversed images to the original batch by concatenating along the batch dimension
        all_image = torch.cat((images, rev_image), dim=0)
        
        return (rev_image, all_image,)
    
class StackImages:
    '''
    Stack Images and Extract Last Image
    
    Stacks the input images with optional previous images and extracts the last image from the input images.
    
    Inputs:
    images              - Source Images
    last_images_in      - Optional input images to prepend
    
    Outputs:
    all_images          - Concatenated images (last_images_in + images, or images if last_images_in is None)
    last_image          - Last image from the input images
    '''
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE", {
                    "default": None,
                }),
            },
            "optional": {
                "last_images_in": ("IMAGE", {
                    "default": None,
                }),
            },
        }
        
    RETURN_TYPES = ("IMAGE", "IMAGE", )
    RETURN_NAMES = ("all_images", "last_image", )
    FUNCTION = "stack_images"
    CATEGORY = cat_image
    
    def stack_images(self, images, last_images_in=None):
        # Ensure images is a torch tensor
        if not isinstance(images, torch.Tensor):
            raise ValueError("Input 'images' must be a torch.Tensor")
        
        if images.ndim == 3:
            images = images.unsqueeze(0)
        if last_images_in is not None and last_images_in.ndim == 3:
            last_images_in = last_images_in.unsqueeze(0)
        
        last_image = images[-1:]  # (1, H, W, C)
        
        if last_images_in is not None:
            all_images = torch.cat((last_images_in, images), dim=0)
        else:
            all_images = images
        
        if all_images.ndim == 3:
            all_images = all_images.unsqueeze(0)
        if last_image.ndim == 3:
            last_image = last_image.unsqueeze(0)
        
        return (all_images, last_image,)
       
class FlatColorQuantization:
    '''
    Flat Color Quantization
    
    https://github.com/mirabarukaso/flat_color_quantization
    
    Inputs:
    image               - Source Image
    
    Outputs:
    out_image           - Quantizated image
    '''
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE", {
                    "default": None,
                }),
                "n_colors": ("INT", {
                    "default": 2048, 
                    "min": 2, 
                    "max": 16384,
                    "step": 1
                }),
                "block_size": ("INT", {
                    "default": 512, 
                    "min": 64, 
                    "max": 2048,
                    "step": 64
                }),
                "temperature": ("FLOAT", {
                    "default": 2, 
                    "min": 1, 
                    "max": 10,
                    "step": 0.05
                }),
                "spatial_scale": ("INT", {
                    "default": 80, 
                    "min": 1, 
                    "max": 300,
                    "step": 1
                }),
                "sharpen": ("FLOAT", {
                    "default": 0, 
                    "min": 0, 
                    "max": 3,
                    "step": 0.1
                }),
            },
        }
        
    RETURN_TYPES = ("IMAGE", )
    RETURN_NAMES = ("out_image",)
    FUNCTION = "FlatColorQuantizationEx"
    CATEGORY = cat_image
    
    def FlatColorQuantizationEx(self, image, n_colors, block_size, temperature, spatial_scale, sharpen):
        img = ConvertToNP(image)
        result = flat_color_multi_scale(image_input=img, n_colors=n_colors, block_size=block_size, 
                                        spatial_scale=spatial_scale, temperature=temperature, sharpen_strength=sharpen)
        
        return(EncodeImage(result),)
    
    