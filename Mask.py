from PIL import Image
import random
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageSequence
from PIL.PngImagePlugin import PngInfo
import numpy as np
import torch
import torch.nn.functional as F
import torchvision.transforms.v2 as T
import re

cat = "Mira/Mask"

def special_match(strg, search=re.compile(r'[^0-9.,;]').search):
    return not bool(search(strg))
   
def RectWidth(Rectangles, Range, nowWidth, warpWidth, y, Width, Height, WarpTimesArray = None):
    warpTimes = 1.0            
    for i in range(Range):            
        if None is not WarpTimesArray:
            warpTimes = float(WarpTimesArray[i])
        if i == (Range -1):
            Rectangles.append([int(nowWidth), y, Width, Height])
        else:
            Rectangles.append([int(nowWidth), y, int(nowWidth + (warpWidth * warpTimes)), Height])
        nowWidth = nowWidth + (warpWidth*warpTimes)
    return Rectangles
    
def RectHeight(Rectangles, Range, nowHeight, warpHeight, x, Width, Height, WarpTimesArray = None):
    warpTimes = 1.0
    for i in range(Range):
        if None is not WarpTimesArray:
            warpTimes = float(WarpTimesArray[i])
        if i == (Range -1):
            Rectangles.append([x, int(nowHeight), Width, Height])    
        else:
            Rectangles.append([x, int(nowHeight), Width, int(nowHeight + (warpHeight * warpTimes))])
        nowHeight = nowHeight + (warpHeight * warpTimes)
    return Rectangles
    
def CreatePNG(Width, Height, Rows, Colums, Colum_first, Layout, DebugMessage):
    DebugMessage += 'Mira:\nLayout:' + Layout + '\n'
    Rectangles = []
    BlocksCount = Rows * Colums
    
    nowWidth = 0
    nowHeight = 0
    warpWidth = 0
    warpHeight = 0
    
    autogen_mark = Layout.find('@')
    if -1 != autogen_mark:
        Layout = Layout[(autogen_mark+1):]    
    
    # , == seperate row
    # ; == seperate colum, has higher prority to cut masks
    # Colum_first == swap , and ;
    if False == special_match(Layout):
        #print('Mira: syntaxerror in layout -> [' + Layout + '] Will use Rows * Colums')
        DebugMessage += 'syntaxerror in layout -> [' + Layout + '] Will use Rows * Colums\n'
        
        new_layout = ''
        for _ in range(Rows):
            new_layout += '1,'
            for _ in range(Colums):
                new_layout += '1,'
            new_layout = new_layout[:-1] + ';'
        new_layout = new_layout[:-1]
        DebugMessage += 'new_layout: ' + new_layout + '\n'
        return CreatePNG(Width, Height, Rows, Colums, Colum_first, new_layout, DebugMessage)
    else:        
        DebugMessage += 'use Layouts\n'
        isSingleSeparator = False
        
        BlocksCount = 0
        WarpTimesArray = 0
            
        if ',' in Layout and ';' not in Layout:
            DebugMessage += 'Mira: only , \n'
            BlocksCount = Layout.count(',') + 1
            WarpTimesArray = Layout.split(',')
            isSingleSeparator = True
        elif ';' in Layout and ',' not in Layout:
            DebugMessage += 'Mira: only ; \n'
            BlocksCount = Layout.count(';') + 1
            WarpTimesArray = Layout.split(';')
            isSingleSeparator = True
        else:            
            DebugMessage += 'Mira: both , ; \n'
            
        if True == isSingleSeparator:            
            SingleBlock = 0
            for WarpTimes in WarpTimesArray:
                SingleBlock += float(WarpTimes)
                
            if True == Colum_first:
                warpWidth = int(Width / SingleBlock)                
                Rectangles = RectWidth(Rectangles, BlocksCount, nowWidth, warpWidth, 0, Width, Height, WarpTimesArray)                
            else:
                warpHeight = int(Height / SingleBlock)                
                Rectangles = RectHeight(Rectangles, BlocksCount, nowHeight, warpHeight, 0, Width, Height, WarpTimesArray)
        else:
            GreatCuts = Layout.split(';')
            GreatBlockArray = []
            GreatBlock = 0
            GreatBlockCounts = 0
            for cut in GreatCuts:
                GreatBlock += float(cut.split(',')[0])
                GreatBlockCounts += 1
                GreatBlockArray.append(cut.split(',')[0])
                
            if True == Colum_first:
                GreatWarpHeight = int(Height / GreatBlock)
                #Rectangles = RectHeight(Rectangles, GreatBlockCounts, nowHeight, GreatWarpHeight, 0, Width, Height, GreatBlockArray)
                #BlocksCount += GreatBlockCounts
                
                now_cut = 0
                for cut in GreatCuts:
                    SingleBlock = 0
                    FullWarpTimesArray = cut.split(',')
                    nowHeightEnd = int(nowHeight+GreatWarpHeight*float(GreatBlockArray[now_cut]))
                                        
                    if now_cut == (len(GreatCuts) - 1):
                        nowHeightEnd = Height
                    
                    if 1 >= len(FullWarpTimesArray):
                        #print('Mira: Bypass empty GreatCuts')    
                        DebugMessage += 'Mira: Bypass empty GreatCuts\n'                    
                    else:
                        # remove first Great Cuts Value
                        FullWarpTimesArray.pop(0)

                        CurrentBlocksCount = len(FullWarpTimesArray)
                        for WarpTimes in FullWarpTimesArray:
                            SingleBlock += float(WarpTimes)                                
                        warpWidth = int(Width / SingleBlock)                                        
                        Rectangles = RectWidth(Rectangles, CurrentBlocksCount, nowWidth, warpWidth, nowHeight, Width, nowHeightEnd, FullWarpTimesArray)                                                           
                        BlocksCount += CurrentBlocksCount                    
                    now_cut += 1
                    nowHeight = nowHeightEnd
                    
            else:                
                GreatWarpWidth = int(Width / GreatBlock)
                #Rectangles = RectWidth(Rectangles, GreatBlockCounts, nowWidth, GreatWarpWidth, 0, Width, Height, GreatBlockArray)
                #BlocksCount += GreatBlockCounts
                
                now_cut = 0
                for cut in GreatCuts:
                    SingleBlock = 0
                    FullWarpTimesArray = cut.split(',')
                    nowWidthEnd = int(nowWidth+GreatWarpWidth*float(GreatBlockArray[now_cut]))
                                        
                    if now_cut == (len(GreatCuts) - 1):
                        nowWidthEnd = Width
                    
                    if 1 >= len(FullWarpTimesArray):
                        #print('Mira: By pass empty GreatCuts')
                        DebugMessage += 'Mira: By pass empty GreatCuts\n'
                    else:
                        # remove first Great Cuts Value
                        FullWarpTimesArray.pop(0)

                        CurrentBlocksCount = len(FullWarpTimesArray)
                        for WarpTimes in FullWarpTimesArray:
                            SingleBlock += float(WarpTimes)                                
                        warpHeight = int(Height / SingleBlock)          

                        Rectangles = RectHeight(Rectangles, CurrentBlocksCount, nowHeight, warpHeight, nowWidth, nowWidthEnd, Height, FullWarpTimesArray)                                                           
                        BlocksCount += CurrentBlocksCount                    
                    now_cut += 1
                    nowWidth = nowWidthEnd
    
        PngImage = Image.new("RGBA", [Width, Height])
        PngDraw = ImageDraw.Draw(PngImage)
        
        PngColorMasks = []
        for _ in range(BlocksCount):
            R = random.randrange(0,255) 
            G = random.randrange(0,255) 
            B = random.randrange(0,255) 
            
            # Extremely low probability, but it happens....
            while PngColorMasks.__contains__([R,G,B]):
                R = random.randrange(0,255) 
                G = random.randrange(0,255) 
                B = random.randrange(0,255) 
                
            PngColorMasks.append([R,G,B])
            DebugMessage += '[' + str(R) + ',' + str(G) + ','+ str(B) + '] '
            DebugMessage += '\n'
            #print('[' + str(R) + ',' + str(G) + ','+ str(B) + '] ')
                        
        for i in range(BlocksCount):
            hex_rgb = ' #{:02X}{:02X}{:02X}'.format(PngColorMasks[i][0], PngColorMasks[i][1], PngColorMasks[i][2])
            #print('Mira: [' + str(i) +']Draw ' + str(Rectangles[i]) + ' with ' + str(PngColorMasks[i]) + hex_rgb)
            DebugMessage += '[' + str(i) +']Draw ' + str(Rectangles[i]) + ' with ' + str(PngColorMasks[i]) + hex_rgb +'\n'
            PngDraw.rectangle(Rectangles[i], fill=(PngColorMasks[i][0], PngColorMasks[i][1], PngColorMasks[i][2], 255))
            
        # Add Image Size to last
        Rectangles.append([0,0,Width,Height])
        DebugMessage += '\n'
                
        return PngImage, Rectangles, PngColorMasks, DebugMessage

class CreateRegionalPNGMask:
    '''
    Create a PNG tiled image with Color Mask stack for regional conditioning mask.
    
    Inputs:
    Width       - Image Width
    Height      - Image Height
    Colum_first - A boolean trigger, when enabled, will treat default cut as a horizontal cut.
    Rows        - Low prority, only works when Layout is incorrect.
    Colums      - Low prority, only works when Layout is incorrect.
    Layout      - Refer to Readme.md @https://github.com/mirabarukaso/ComfyUI_Mira
    Use_Catched_PNG - Save PNG to memory for performance
        
    Outputs:
    PngImage        - Image
    PngColorMasks   - A List contains all PNG Blocks' color information.
    PngRectangles   - A List contains all PNG Blocks' rectangle informationm, last one is the whole Image's Width and Height
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
                "Colum_first": ("BOOLEAN", {
                    "default": False
                }),
                "Rows": ("INT", {
                    "default": 1,
                    "min": 1,
                    "step": 1,
                    "display": "number" 
                }),
                "Colums": ("INT", {
                    "default": 1,
                    "min": 1,
                    "step": 1,
                    "display": "number" 
                }),
                "Layout": ("STRING", {
                    "multiline": False, 
                    "default": "1,1,1"
                }),
            },            
        }
                
    RETURN_TYPES = ("IMAGE", "LIST", "LIST", "STRING",)
    RETURN_NAMES = ("PngImage", "PngColorMasks", "PngRectangles", "Debug",)
    FUNCTION = "CreateRegionalPNGMaskEx"
    CATEGORY = cat
    
    def CreateRegionalPNGMaskEx(self, Width, Height, Rows, Colums, Colum_first, Layout = '#'):
        DebugMessage = ''                        
        
        PngImage, PngRectangles, PngColorMasks, DebugMessage = CreatePNG(Width, Height, Rows, Colums, Colum_first, Layout, DebugMessage)
        
        #refer: https://github.com/comfyanonymous/ComfyUI/blob/master/nodes.py#L1487
        #       LoadImage
        output_images = []
        output_masks = []
        for i in ImageSequence.Iterator(PngImage):
            i = ImageOps.exif_transpose(i)
            if i.mode == 'I':
                i = i.point(lambda i: i * (1 / 255))
                
            image = i.convert("RGB")
            image = np.array(image).astype(np.float32) / 255.0
            image = torch.from_numpy(image)[None,]
            
            if 'A' in i.getbands():
                mask = np.array(i.getchannel('A')).astype(np.float32) / 255.0
                mask = 1. - torch.from_numpy(mask)
            else:
                mask = torch.zeros((64,64), dtype=torch.float32, device="cpu")
                
            output_images.append(image)
            output_masks.append(mask.unsqueeze(0))
            
        if len(output_images) > 1:
            output_image = torch.cat(output_images, dim=0)
            output_mask = torch.cat(output_masks, dim=0)
        else:
            output_image = output_images[0]
            output_mask = output_masks[0]            
            
        return (output_image, PngColorMasks, PngRectangles, DebugMessage,)
    
class PngColorMasksToString:
    '''
    Convert specified Index of PngColorMasks to HEX value. 
    
    Inputs:
    PngColorMasks   - List from Create PNG Mask
    Index           - The Block id of PNG Mask
        
    Outputs:
    mask_color      - String. e.g. RGB(255,0,255) to #FF00FF
    '''
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "PngColorMasks": ("LIST", {
                    "display": "input" 
                }),
                "Index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "step": 1,
                    "display": "number" 
                }),
            },
        }
        
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("mask_color",)
    FUNCTION = "ColorMasksToStringEx"
    CATEGORY = cat
    
    def ColorMasksToStringEx(self, PngColorMasks, Index):        
        if len(PngColorMasks) <= Index:
            print('Mira: ERROR Index is greater than Mask count! Will use 0')
            Index = 0
        
        ret = ('#{:02X}{:02X}{:02X}'.format(PngColorMasks[Index][0], PngColorMasks[Index][1], PngColorMasks[Index][2]))
        return (ret,)
    
class PngColorMasksToRGB:
    '''
    Convert specified Index of PngColorMasks to RGB value. 
    
    Inputs:
    PngColorMasks   - List from Create PNG Mask
    Index           - The Block id of PNG Mask
        
    Outputs:
    R               - Integer. Red
    G               - Integer. Green
    B               - Integer. Blue
    '''
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "PngColorMasks": ("LIST", {
                    "display": "input" 
                }),
                "Index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "step": 1,
                    "display": "number" 
                }),
            },
        }
        
    RETURN_TYPES = ("INT","INT","INT",)
    RETURN_NAMES = ("R", "G", "B", )
    FUNCTION = "ColorMasksToRGBEx"
    CATEGORY = cat
    
    def ColorMasksToRGBEx(self, PngColorMasks, Index):        
        if len(PngColorMasks) <= Index:
            print('Mira: ERROR Index is greater than Mask count! Will use 0')
            Index = 0
            
        R = PngColorMasks[Index][0]                             
        G = PngColorMasks[Index][1]
        B = PngColorMasks[Index][2]
        return (R, G, B,)
    
class PngColorMasksToStringList:
    '''
    Convert ranged PngColorMasks to HEX value.
    
    Inputs:
    PngColorMasks   - List from Create PNG Mask
    Start_At_Index  - The first Block id to start
        
    Outputs:
    mask_color[0-9] - String. e.g. RGB(255,0,255) to #FF00FF
    '''
    @classmethod
    def INPUT_TYPES(s):
        inputs = {
            "required": {
                "PngColorMasks": ("LIST", {
                    "display": "input" 
                }),
                "Start_At_Index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 256,
                    "step": 1,
                    "display": "number" 
                }),
            }
        }
        
        return inputs

    # Not sure if there's a dynamic outputs solution....
    r_t = ()
    r_n = ()
    for i in range(10):        
        r_t += ('STRING',)
        r_n += (f'mask_color_{i}',)
    
    RETURN_TYPES = r_t
    RETURN_NAMES = r_n
    FUNCTION = "ColorMasksToStringListEx"
    CATEGORY = cat    
    
    def ColorMasksToStringListEx(self, PngColorMasks, Start_At_Index):        
        ret = []
        for Index in range(Start_At_Index, Start_At_Index + 10, 1):            
            if len(PngColorMasks) <= Index:
                ret.append('#000000')
            else:
                ret.append('#{:02X}{:02X}{:02X}'.format(PngColorMasks[Index][0], PngColorMasks[Index][1], PngColorMasks[Index][2]))
                
        return (ret[0],ret[1],ret[2],ret[3],ret[4],ret[5],ret[6],ret[7],ret[8],ret[9],)
    
class PngColorMasksToMaskList:
    '''
    Convert ranged PngColorMasks to Mask with Mask Blur function.
    This is a color based function, so it could NOT set Intenisity to Mask.
    
    Inputs:
    PngImage        - Image from Create PNG Mask
    PngColorMasks   - List from Create PNG Mask
    Blur            - The amount of Blur, 0 for Soild.
    Start_At_Index  - The first Block id to start
        
    Outputs:
    mask_[0-9]      - Mask for anyone who want a Mask
    '''
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "PngImage": ("IMAGE", {
                    "display": "input" 
                }),
                "PngColorMasks": ("LIST", {
                    "display": "input" 
                }),
                "Blur": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "step": 0.5,
                    "display": "number" 
                }),
                "Start_At_Index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "step": 1,
                    "display": "number" 
                }),
            },
        }
        
        # Not sure if there's a dynamic outputs solution....
    r_t = ()
    r_n = ()
    for i in range(10):        
        r_t += ('MASK',)
        r_n += (f'mask_{i}',)
            
    RETURN_TYPES = r_t
    RETURN_NAMES = r_n
    FUNCTION = "ColorMasksToMaskListEx"
    CATEGORY = cat
    
    # refer: https://github.com/cubiq/ComfyUI_essentials
    # MaskBlur and MaskFromColor
    def ColorMasksToMaskListEx(self, PngImage, PngColorMasks, Blur, Start_At_Index):
        masks = []
                
        for index in range(Start_At_Index, Start_At_Index + 10, 1):            
            if len(PngColorMasks) <= index:
                color = torch.tensor([0,0,0])
            else:
                color = torch.tensor(PngColorMasks[index])
            temp = (torch.clamp(PngImage, 0, 1.0) * 255.0).round().to(torch.int)
            lower_bound = (color).clamp(min=0)
            upper_bound = (color).clamp(max=255)
            mask = (temp >= lower_bound) & (temp <= upper_bound)
            mask = mask.all(dim=-1)
            mask = mask.float()
            
            if 0 < Blur:
                size = int(6 * Blur +1)
                if size % 2 == 0:
                    size+= 1
                
                blurred = mask.unsqueeze(1)
                blurred = T.GaussianBlur(size, Blur)(blurred)
                blurred = blurred.squeeze(1)
                mask = blurred
            
            masks.append(mask)

        return (masks[0], masks[1], masks[2], masks[3], masks[4], masks[5], masks[6], masks[7], masks[8], masks[9],)
    
    
# refer: https://github.com/comfyanonymous/ComfyUI
# SolidMask
# refer: https://github.com/cubiq/ComfyUI_essentials
# MaskBlur MaskBatch    
def CreateMaskFromPngRectangles(PngRectangles, Intenisity, Blur, Start_At_Index, End_At_Step=1):
    masks = []       

    sizePngRectangles = len(PngRectangles) - 1
    Width = PngRectangles[sizePngRectangles][2]
    Height = PngRectangles[sizePngRectangles][3]    

    destinationMask = torch.full((1,Height, Width), 0, dtype=torch.float32, device="cpu")       
                    
    for index in range(Start_At_Index, End_At_Step, 1):     
        # In case of someone need a whole mask, changed <= to <
        if sizePngRectangles < index:
            mask = destinationMask
        else:
            W = PngRectangles[index][2] - PngRectangles[index][0]
            H = PngRectangles[index][3] - PngRectangles[index][1]
            output = destinationMask.reshape((-1, destinationMask.shape[-2], destinationMask.shape[-1])).clone()
            
            sourceMask = torch.full((1,H, W), Intenisity, dtype=torch.float32, device="cpu")
            source = sourceMask.reshape((-1, sourceMask.shape[-2], sourceMask.shape[-1]))
            
            left, top = (PngRectangles[index][0],PngRectangles[index][1],)
            right, bottom = (min(left + source.shape[-1], destinationMask.shape[-1]), min(top + source.shape[-2], destinationMask.shape[-2]))
            visible_width, visible_height = (right - left, bottom - top,)
            
            source_portion = source[:, :visible_height, :visible_width]
            destination_portion = destinationMask[:, top:bottom, left:right]
            
            # Add
            output[:, top:bottom, left:right] = destination_portion + source_portion
            
            mask = output
        
            if 0 < Blur:
                size = int(6 * Blur +1)
                if size % 2 == 0:
                    size+= 1
                
                blurred = mask.unsqueeze(1)
                blurred = T.GaussianBlur(size, Blur)(blurred)
                blurred = blurred.squeeze(1)
                mask = blurred
        
        masks.append(mask)
    return masks
        
class PngRectanglesToMask:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "PngRectangles": ("LIST", {
                    "display": "input" 
                }),
                "Intenisity": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.1,
                    "display": "number" 
                }),
                "Blur": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "step": 0.5,
                    "display": "number" 
                }),
                "Start_At_Index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "step": 1,
                    "display": "number" 
                }),
            },
        }
                    
    RETURN_TYPES = ('MASK',)
    RETURN_NAMES = ('mask',)
    FUNCTION = "PngRectanglesToMaskEx"
    CATEGORY = cat
    
    def PngRectanglesToMaskEx(self, PngRectangles, Intenisity, Blur, Start_At_Index):
        masks = CreateMaskFromPngRectangles(PngRectangles, Intenisity, Blur, Start_At_Index, Start_At_Index + 1)
        return (masks[0],)    
    
class PngRectanglesToMaskList:
    '''
    Convert ranged PngRectangles to Mask with Mask Intenisity and Blur function.
    This function creates Mask directly from Rectangles data.
    
    Inputs:
    PngRectangles   - List from Create PNG Mask
    Intenisity      - The intenisity of Mask, 1 for Soild.
    Blur            - The amount of Blur, 0 for Soild.
    Start_At_Index  - The first Block id to start
        
    Outputs:
    mask_[0-9]      - Mask for anyone who want a Mask
    '''
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "PngRectangles": ("LIST", {
                    "display": "input" 
                }),
                "Intenisity": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.1,
                    "display": "number" 
                }),
                "Blur": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "step": 0.5,
                    "display": "number" 
                }),
                "Start_At_Index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "step": 1,
                    "display": "number" 
                }),
            },
        }
        
    # Not sure if there's a dynamic outputs solution....
    r_t = ()
    r_n = ()
    for i in range(10):        
        r_t += ('MASK',)
        r_n += (f'mask_{i}',)
            
    RETURN_TYPES = r_t
    RETURN_NAMES = r_n
    FUNCTION = "PngRectanglesToMaskListEx"
    CATEGORY = cat

    def PngRectanglesToMaskListEx(self, PngRectangles, Intenisity, Blur, Start_At_Index):
        masks = CreateMaskFromPngRectangles(PngRectangles, Intenisity, Blur, Start_At_Index, Start_At_Index + 10)

        return (masks[0], masks[1], masks[2], masks[3], masks[4], masks[5], masks[6], masks[7], masks[8], masks[9],)
    
    
class CreateMaskWithCanvas:    
    '''
    Create a new mask on defined cavans
    
    Inputs:
    C_Width         - Width of cavans
    C_Height        - Height of cavans
    X               - The left point of new mask on cavans
    Y               - The top point of new mask on cavans
    Width           - Mask width
    Height          - Mask height
    Intenisity      - The intenisity of Mask, 1 for Soild.
    Blur            - The amount of Blur, 0 for Soild.    
        
    Outputs:
    mask            - New mask with defined cavans
    '''
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "C_Width": ("INT", { "default": 512, "min": 8, "max": 4096, "step": 1, "display": "number" }),
                "C_Height": ("INT", { "default": 512, "min": 8, "max": 4096, "step": 1, "display": "number" }),                
                "X": ("INT", { "default": 0, "min": 0, "max": 4096, "step": 1, "display": "number" }),
                "Y": ("INT", { "default": 0, "min": 0, "max": 4096, "step": 1, "display": "number" }),
                "Width": ("INT", { "default": 512, "min": 8, "max": 4096, "step": 1, "display": "number" }),
                "Height": ("INT", { "default": 512, "min": 8, "max": 4096, "step": 1, "display": "number" }),                
                "Intenisity": ("FLOAT", { "default": 1.0, "min": 0.0, "max": 1.0, "step": 0.1, "display": "number" }),
                "Blur": ("FLOAT", { "default": 0.0, "min": 0.0, "step": 0.5, "display": "number" }),
            },
        }
        
    RETURN_TYPES = ('MASK',)
    RETURN_NAMES = ('mask',)
    FUNCTION = "CreateMaskWithCanvasEx"
    CATEGORY = cat
    
    
    def CreateMaskWithCanvasEx(self, C_Width, C_Height, X, Y, Width, Height, Intenisity, Blur):       
        destinationMask = torch.full((1,C_Height, C_Width), 0, dtype=torch.float32, device="cpu")
        
        output = destinationMask.reshape((-1, destinationMask.shape[-2], destinationMask.shape[-1])).clone()
        
        sourceMask = torch.full((1, Height, Width), Intenisity, dtype=torch.float32, device="cpu")
        source = sourceMask.reshape((-1, sourceMask.shape[-2], sourceMask.shape[-1]))
        
        left, top = (X, Y)
        right, bottom = (min(left + source.shape[-1], destinationMask.shape[-1]), min(top + source.shape[-2], destinationMask.shape[-2]))
        visible_width, visible_height = (right - left, bottom - top,)
        
        source_portion = source[:, :visible_height, :visible_width]
        destination_portion = destinationMask[:, top:bottom, left:right]
        
        output[:, top:bottom, left:right] = destination_portion + source_portion            
        mask = output
    
        if 0 < Blur:
            size = int(6 * Blur +1)
            if size % 2 == 0:
                size+= 1
            
            blurred = mask.unsqueeze(1)
            blurred = T.GaussianBlur(size, Blur)(blurred)
            blurred = blurred.squeeze(1)
            mask = blurred

        return (mask,)
    
    