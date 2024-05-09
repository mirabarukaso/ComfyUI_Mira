import math
import random
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageSequence
from PIL.PngImagePlugin import PngInfo
import numpy as np
import torch
import torch.nn.functional as F
import torchvision.transforms.v2 as T
import re

cat = "Mira/Mask"

def combine_mask(masks):
    if len(masks) > 0:
        if 1 == len(masks) :
            final_mask = masks[0]
        else:
            final_mask = masks[0]
            for index in range(1, len(masks)):
                output = final_mask.reshape((-1, final_mask.shape[-2], final_mask.shape[-1])).clone()
                
                left, top = (0, 0)
                right, bottom = (min(left + final_mask.shape[-1], masks[index].shape[-1]), min(top + final_mask.shape[-2], masks[index].shape[-2]))
                visible_width, visible_height = (right - left, bottom - top,)

                source_portion = final_mask[:, :visible_height, :visible_width]
                destination_portion = masks[index][:, top:bottom, left:right]

                output[:, top:bottom, left:right] = destination_portion + source_portion    
                
                final_mask = output     
    else:
        # dummy
        final_mask = create_mask_with_canvas(0, 0, 0, 0, 8, 8, 0, 0)
    
    return final_mask

def mask_blur(blur, mask):
    # refer: https://github.com/cubiq/ComfyUI_essentials
    # MaskBlur MaskBatch  
    if 0 < blur:
            size = int(6 * blur +1)
            if size % 2 == 0:
                size+= 1
            
            blurred = mask.unsqueeze(1)
            blurred = T.GaussianBlur(size, blur)(blurred)
            blurred = blurred.squeeze(1)
            new_mask = blurred
    else:
        new_mask = mask
        
    return new_mask

def create_mask_with_canvas(C_Width, C_Height, X, Y, Width, Height, Intenisity, Blur):       
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
    mask = mask_blur(Blur, output)
    
    return mask

def special_match(strg, search=re.compile(r'[^0-9.,;]').search):
    return not bool(search(strg))
   
def RectWidth(Rectangles, BlocksCount, nowWidth, warpWidth, y, Width, Height, WarpTimesArray = None):
    warpTimes = 1.0
    for i in range(BlocksCount):
        if None is not WarpTimesArray:
            warpTimes = float(WarpTimesArray[i])
        if i == (BlocksCount -1):
            Rectangles.append([int(nowWidth), y, Width, Height])
        else:
            Rectangles.append([int(nowWidth), y, int(nowWidth + (warpWidth * warpTimes)), Height])
        nowWidth = nowWidth + (warpWidth*warpTimes)
    return Rectangles
    
def RectHeight(Rectangles, BlocksCount, nowHeight, warpHeight, x, Width, Height, WarpTimesArray = None):
    warpTimes = 1.0
    for i in range(BlocksCount):
        if None is not WarpTimesArray:
            warpTimes = float(WarpTimesArray[i])
        if i == (BlocksCount -1):
            Rectangles.append([x, int(nowHeight), Width, Height])    
        else:
            Rectangles.append([x, int(nowHeight), Width, int(nowHeight + (warpHeight * warpTimes))])
        nowHeight = nowHeight + (warpHeight * warpTimes)
    return Rectangles
    
def DrawPNG(Width, Height, BlocksCount, DebugMessage, Rectangles):
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

    return PngImage, PngColorMasks, Rectangles, DebugMessage

def CreateTillingPNG(Width, Height, Rows, Colums, Colum_first, Layout, DebugMessage):
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
        return CreateTillingPNG(Width, Height, Rows, Colums, Colum_first, new_layout, DebugMessage)
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
            # ratio
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
                    # ratio
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

        #Draw PNG
        PngImage, PngColorMasks, PngRectangles, DebugMessage = DrawPNG(Width, Height, BlocksCount, DebugMessage, Rectangles)
                            
        return PngImage, PngRectangles, PngColorMasks, DebugMessage

def CreateNestedPNG(Width, Height, X, Y, unlimit_top, unlimit_bottom, unlimit_left, unlimit_right, Layout, DebugMessage):
    DebugMessage += 'Mira:\nLayout:' + Layout + '\n'
    
    autogen_mark = Layout.find('@')
    if -1 != autogen_mark:
        Layout = Layout[(autogen_mark+1):]    
    
    if False == special_match(Layout):
        DebugMessage += 'syntaxerror in layout -> [' + Layout + '] Will use [1,1]\n'
        Layout = '1,1'
    
    DebugMessage += 'use Layouts\n'
        
    BlocksCount = 0
    WarpTimesArray = 0
            
    if ',' in Layout and ';' not in Layout:
        DebugMessage += 'only , \n'
        BlocksCount = Layout.count(',') + 1
        WarpTimesArray = Layout.split(',')
    elif ';' in Layout and ',' not in Layout:
        DebugMessage += 'only ; \n'
        BlocksCount = Layout.count(';') + 1
        WarpTimesArray = Layout.split(';')
    else:            
        DebugMessage += 'both [, ;] but we will stop at [;]\n'
        New_Layout = Layout.split(';')[0]
        DebugMessage += 'Use [' + New_Layout + ']\n'
        Layout = New_Layout
        
        BlocksCount = Layout.count(',') + 1
        WarpTimesArray = Layout.split(',')
        
    if X > Width:
        X = Width
        
    if Y > Height:
        Y = Height    
        
    # First the whole canvas
    Rectangles = []
    Rectangle = [0 ,0, Width, Height]
    Rectangles.append(Rectangle)
    
    last_width = Width
    last_height = Height
                
    # ratio
    SingleBlock = 0
    for WarpTimes in WarpTimesArray:
        SingleBlock += float(WarpTimes)
        
    warpWidth = int(Width / SingleBlock)
    warpHeight = int(Height / SingleBlock)
        
    # Divide rate, the canvas(1st one) is always 1
    for i in range(BlocksCount):
        # 0.1
        if 0 > float(WarpTimesArray[i]):
            WarpTimesArray[i] = '0.1'    
            
        current_width = last_width - int(warpWidth * float(WarpTimesArray[i]))                                    
        current_height = last_height - int(warpHeight * float(WarpTimesArray[i]))
        
        DebugMessage += 'SingleBlock [' + str(i) + '] = ' + str(SingleBlock) + '\n'
        DebugMessage += 'last_width [' + str(i) + '] = ' + str(last_width) + '\n'
        DebugMessage += 'last_height [' + str(i) + '] = ' + str(last_height) + '\n'
        
        last_width = current_width
        last_height = current_height
                
        real_x = X - int(current_width/2)
        real_y = Y - int(current_height/2)
        
        left = real_x
        top = real_y
        right = X + int(current_width/2)
        bottom = Y + int(current_height/2)       
                
        if True == unlimit_top:
            top = 0
        if True == unlimit_bottom:
            bottom = Height
        if True == unlimit_left:
            left = 0
        if True == unlimit_right:
            right = Width
        
        Rectangle = [left ,top, right, bottom]        
        Rectangles.append(Rectangle)        
            
    PngImage, PngColorMasks, PngRectangles, DebugMessage = DrawPNG(Width, Height, BlocksCount, DebugMessage, Rectangles)   
    
    return PngImage, PngRectangles, PngColorMasks, DebugMessage

def LoadImagePNG(PngImage):
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
        
    return output_image

class CreateTillingPNGMask:
    '''
    Create a tilling PNG image with Color Mask stack for regional conditioning mask.
    
    Inputs:
    Width       - Image Width
    Height      - Image Height
    Colum_first - A boolean trigger, when enabled, will treat default cut as a horizontal cut.
    Rows        - Low prority, only works when Layout is incorrect.
    Colums      - Low prority, only works when Layout is incorrect.
    Layout      - Refer to Readme.md @https://github.com/mirabarukaso/ComfyUI_Mira
        
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
                
    RETURN_TYPES = ("IMAGE", "MIRA_COLOR_LIST", "MIRA_MASKS_LIST", "STRING",)
    RETURN_NAMES = ("PngImage", "PngColorMasks", "PngRectangles", "Debug",)
    FUNCTION = "CreateTillingPNGMaskEx"
    CATEGORY = cat
    
    def CreateTillingPNGMaskEx(self, Width, Height, Rows, Colums, Colum_first, Layout = '#'):
        DebugMessage = ''
        
        PngImage, PngRectangles, PngColorMasks, DebugMessage = CreateTillingPNG(Width, Height, Rows, Colums, Colum_first, Layout, DebugMessage)        
        output_image = LoadImagePNG(PngImage)   
            
        return (output_image, PngColorMasks, PngRectangles, DebugMessage,)

class CreateNestedPNGMask:
    '''
    Create a `Nested Rectangles` PNG image with Color Mask stack for regional conditioning mask.   
    
    Inputs:
    Width           - Image Width.
    Height          - Image Height.
    
    X               - Center X point of all Rectangles.
    Y               - Center Y point of all Rectangles.
    
    unlimit_top     - When `ENABLED`, all `masks` will create from the top of Image.
    unlimit_bottom  - When `ENABLED`, all `masks` will create till the bottom of Image.    
    unlimit_left    - When `ENABLED`, all `masks` will create from the left of Image.
    unlimit_right   - When `ENABLED`, all `masks` will create till the right of Image.
        
    Layout          - Refer to Readme.md @https://github.com/mirabarukaso/ComfyUI_Mira
        
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
                "X": ("INT", {
                    "default": 256,
                    "min": 0,
                    "step": 1,
                    "display": "number" 
                }),
                "Y": ("INT", {
                    "default": 256,
                    "min": 0,
                    "step": 1,
                    "display": "number" 
                }),
                "unlimit_top": ("BOOLEAN", {
                    "default": False
                }),
                "unlimit_bottom": ("BOOLEAN", {
                    "default": False
                }),
                "unlimit_left": ("BOOLEAN", {
                    "default": False
                }),
                "unlimit_right": ("BOOLEAN", {
                    "default": False
                }),
                "Layout": ("STRING", {
                    "multiline": False, 
                    "default": "1,1,1"
                }),
            },            
        }
        
    RETURN_TYPES = ("IMAGE", "MIRA_COLOR_LIST", "MIRA_MASKS_LIST", "STRING",)
    RETURN_NAMES = ("PngImage", "PngColorMasks", "PngRectangles", "Debug",)
    FUNCTION = "CreateNestedRectanglePNGMaskEx"
    CATEGORY = cat
    
    def CreateNestedRectanglePNGMaskEx(self, Width, Height, X, Y, unlimit_top, unlimit_bottom, unlimit_left, unlimit_right, Layout = '#'):
        DebugMessage = ''
        
        PngImage, PngRectangles, PngColorMasks, DebugMessage = CreateNestedPNG(Width, Height, X, Y, unlimit_top, unlimit_bottom, unlimit_left, unlimit_right, Layout, DebugMessage)
        output_image = LoadImagePNG(PngImage)   
        
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
                "PngColorMasks": ("MIRA_COLOR_LIST", {
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
            #print('Mira: ERROR Index is greater than Mask count! Will use 0')
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
                "PngColorMasks": ("MIRA_MASKS_LIST", {
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
            #print('Mira: ERROR Index is greater than Mask count! Will use 0')
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
                "PngColorMasks": ("MIRA_COLOR_LIST", {
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
                "PngColorMasks": ("MIRA_COLOR_LIST", {
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
    
    
    def ColorMasksToMaskListEx(self, PngImage, PngColorMasks, Blur, Start_At_Index):
        # refer: https://github.com/cubiq/ComfyUI_essentials
        # MaskFromColor
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
                        
            mask = mask_blur(Blur, mask)
            
            masks.append(mask)

        return (masks[0], masks[1], masks[2], masks[3], masks[4], masks[5], masks[6], masks[7], masks[8], masks[9],)
    
    
def CombineMask(destination, source, x, y, operation):
    # refer: https://github.com/comfyanonymous/ComfyUI
    # MaskComposite    
    output = destination.reshape((-1, destination.shape[-2], destination.shape[-1])).clone()
    source = source.reshape((-1, source.shape[-2], source.shape[-1]))

    left, top = (x, y,)
    right, bottom = (min(left + source.shape[-1], destination.shape[-1]), min(top + source.shape[-2], destination.shape[-2]))
    visible_width, visible_height = (right - left, bottom - top,)

    source_portion = source[:, :visible_height, :visible_width]
    destination_portion = destination[:, top:bottom, left:right]

    if operation == "multiply":
        output[:, top:bottom, left:right] = destination_portion * source_portion
    elif operation == "add":
        output[:, top:bottom, left:right] = destination_portion + source_portion
    elif operation == "subtract":
        output[:, top:bottom, left:right] = destination_portion - source_portion
    elif operation == "and":
        output[:, top:bottom, left:right] = torch.bitwise_and(destination_portion.round().bool(), source_portion.round().bool()).float()
    elif operation == "or":
        output[:, top:bottom, left:right] = torch.bitwise_or(destination_portion.round().bool(), source_portion.round().bool()).float()
    elif operation == "xor":
        output[:, top:bottom, left:right] = torch.bitwise_xor(destination_portion.round().bool(), source_portion.round().bool()).float()

    output = torch.clamp(output, 0.0, 1.0)

    return output

def CreateMask(PngRectangles, index, destinationMask, Intenisity, Blur):
    # refer: https://github.com/comfyanonymous/ComfyUI
    # SolidMask
    W = PngRectangles[index][2] - PngRectangles[index][0]
    H = PngRectangles[index][3] - PngRectangles[index][1]
    output = destinationMask.reshape((-1, destinationMask.shape[-2], destinationMask.shape[-1])).clone()
    
    sourcemask = torch.full((1,H, W), Intenisity, dtype=torch.float32, device="cpu")
    source = sourcemask.reshape((-1, sourcemask.shape[-2], sourcemask.shape[-1]))
    
    left, top = (PngRectangles[index][0],PngRectangles[index][1],)
    right, bottom = (min(left + source.shape[-1], destinationMask.shape[-1]), min(top + source.shape[-2], destinationMask.shape[-2]))
    visible_width, visible_height = (right - left, bottom - top,)
    
    source_portion = source[:, :visible_height, :visible_width]
    destination_portion = destinationMask[:, top:bottom, left:right]
    
    output[:, top:bottom, left:right] = destination_portion + source_portion
                
    mask = mask_blur(Blur, output)        
    
    return mask
  
def CreateMaskFromPngRectangles(PngRectangles, Intenisity, Blur, Start_At_Index, End_At_Step=1):
    masks = []       

    sizePngRectangles = len(PngRectangles) - 1
    Width = PngRectangles[sizePngRectangles][2]
    Height = PngRectangles[sizePngRectangles][3]    
    
    #print("sizePngRectangles = " + str(sizePngRectangles))
    destinationMask = torch.full((1,Height, Width), 0, dtype=torch.float32, device="cpu")       
    
    # Check Tilling or Nested
    if PngRectangles[0] == PngRectangles[sizePngRectangles]:
        # remove the latest one
        sizePngRectangles = len(PngRectangles) - 2
        # Nested
        for index in range(Start_At_Index, End_At_Step, 1):     
            if sizePngRectangles < index:
                mask = destinationMask
            elif sizePngRectangles == index:
                # create full mask
                mask = mask = CreateMask(PngRectangles, 0, destinationMask, Intenisity, Blur)
            else:
                if (sizePngRectangles - 1) == index:
                    # print("index = " + str(index))
                    mask = CreateMask(PngRectangles, index, destinationMask, Intenisity, Blur)                
                else:
                    mask_dest = CreateMask(PngRectangles, index, destinationMask, Intenisity, Blur)
                    mask_src = CreateMask(PngRectangles, index + 1, destinationMask, Intenisity, Blur)                    
                    mask = CombineMask(mask_dest, mask_src, 0, 0, 'subtract')
            masks.append(mask)
    else:      
        # Tilling                  
        for index in range(Start_At_Index, End_At_Step, 1):     
            # In case of someone need a whole mask, changed <= to <
            if sizePngRectangles < index:
                mask = destinationMask
            else:
                mask = CreateMask(PngRectangles, index, destinationMask, Intenisity, Blur)
            
            masks.append(mask)
    return masks
        
class PngRectanglesToMask:
    '''
    Convert PngRectangles to selected Mask with Mask Intenisity and Blur function.
    This function creates Mask directly from Rectangles data.
    
    Inputs:
    PngRectangles   - List from Create PNG Mask
    Intenisity      - The intenisity of Mask, 1 for Soild.
    Blur            - The amount of Blur, 0 for Soild.
    Start_At_Index  - The first Block id to start
    Overlap         - Combine the `Previous` or `Next` Masks into current Mask. `None` for disable.
    Overlap_Count   - How many `Previous` or `Next` Masks you want to combine.
        
    Outputs:
    mask            - Mask for anyone who want a Mask
    '''
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "PngRectangles": ("MIRA_MASKS_LIST", {
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
                "Overlap": (["None", "Previous", "Next"], {"display": "string"}),
                "Overlap_Count": ("INT", {
                    "default": 1,
                    "min": 1,
                    "step": 1,
                    "display": "number" 
                }),
            },
        }
                    
    RETURN_TYPES = ('MASK',)
    RETURN_NAMES = ('mask',)
    FUNCTION = "PngRectanglesToMaskEx"
    CATEGORY = cat
    
    def PngRectanglesToMaskEx(self, PngRectangles, Intenisity, Blur, Start_At_Index, Overlap, Overlap_Count):
        if "Previous" == Overlap:
            if 0 == Start_At_Index:
                masks = CreateMaskFromPngRectangles(PngRectangles, Intenisity, Blur, Start_At_Index, Start_At_Index + 1)
                final_mask = masks[0]
            else:
                tmp_index = Start_At_Index - Overlap_Count
                if(tmp_index < 0):
                    tmp_index = 0
                masks = CreateMaskFromPngRectangles(PngRectangles, Intenisity, Blur, tmp_index, Start_At_Index + 1)
                final_mask = combine_mask(masks)
        elif "Next" == Overlap:
            sizePngRectangles = len(PngRectangles) - 1
            tmp_index = Start_At_Index + Overlap_Count + 1
            if(tmp_index > sizePngRectangles):
                tmp_index = sizePngRectangles
            masks = CreateMaskFromPngRectangles(PngRectangles, Intenisity, Blur, Start_At_Index, tmp_index)
            final_mask = combine_mask(masks)
        else:
            masks = CreateMaskFromPngRectangles(PngRectangles, Intenisity, Blur, Start_At_Index, Start_At_Index + 1)
            final_mask = masks[0]
                    
        return (final_mask,)    
    
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
                "PngRectangles": ("MIRA_MASKS_LIST", {
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
        mask = create_mask_with_canvas(C_Width, C_Height, X, Y, Width, Height, Intenisity, Blur)        
        return (mask,)
    
class CreateWatermarkRemovalMask:
    '''
    Creates multiple masks at the corners of the image for subsequent watermark detection and removal.
    
    Inputs:
    C_Width         - Width of cavans.
    C_Height        - Height of cavans.
    
    Mask_W          - Mask width, maxium value are half of cavans width.
    Mask_H          - Mask height, maxium value are half of cavans height.
    
    Top_L           - Create mask from top left.
    Top_R           - Create mask from top right.
    Bottom_L        - Create mask from bottom left.
    Bottom_R        - Create mask from bottom right.    
    
    EdgeToEdge      - Preserve the N pixels at the outermost edges of the image to prevent image noise.  Set to 0 for borderless.
    
    Intenisity      - The intenisity of Mask, 1 for Soild.
    Blur            - The amount of Blur, 0 for Soild.    
        
    Output:
    Mask            - New mask with defined cavans.
    '''
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "C_Width": ("INT", { "default": 512, "min": 8, "max": 4096, "step": 1, "display": "number" }),
                "C_Height": ("INT", { "default": 512, "min": 8, "max": 4096, "step": 1, "display": "number" }),                                
                "Mask_W": ("INT", { "default": 512, "min": 8, "max": 4096, "step": 1, "display": "number" }),
                "Mask_H": ("INT", { "default": 512, "min": 8, "max": 4096, "step": 1, "display": "number" }),
                
                "Top_L": ("BOOLEAN", {"default": False}),
                "Top_R": ("BOOLEAN", {"default": False}),
                "Bottom_L": ("BOOLEAN", {"default": True}),
                "Bottom_R": ("BOOLEAN", {"default": False}),                
                
                "EdgeToEdge": ("INT", { "default": 1, "min": 0, "max": 16, "step": 1, "display": "number" }),
                                
                "Intenisity": ("FLOAT", { "default": 1.0, "min": 0.0, "max": 1.0, "step": 0.1, "display": "number" }),
                "Blur": ("FLOAT", { "default": 0.0, "min": 0.0, "step": 0.5, "display": "number" }),
            },
        }
        
    RETURN_TYPES = ('MASK',)
    RETURN_NAMES = ('Mask',)
    FUNCTION = "CreateWatermarkRemovalMaskEx"
    CATEGORY = cat
    
    def CreateWatermarkRemovalMaskEx(self, C_Width, C_Height, Mask_W, Mask_H, Top_L, Top_R, Bottom_L, Bottom_R, EdgeToEdge, Intenisity, Blur):      
        if (Mask_W*2) > C_Width:
            Mask_W = C_Width / 2
        
        if (Mask_H*2) > C_Height:
            Mask_H = C_Height / 2        
                
        masks = []       
        
        if True == Top_L:
            mask = create_mask_with_canvas(C_Width, C_Height, 0 + EdgeToEdge, 0 + EdgeToEdge, Mask_W, Mask_H, Intenisity, Blur)
            masks.append(mask)
            
        if True == Top_R:
            mask = create_mask_with_canvas(C_Width, C_Height, C_Width - Mask_W - EdgeToEdge, 0 + EdgeToEdge, Mask_W, Mask_H, Intenisity, Blur)
            masks.append(mask)
        
        if True == Bottom_L:
            mask = create_mask_with_canvas(C_Width, C_Height, 0 + EdgeToEdge, C_Height - Mask_H - EdgeToEdge, Mask_W, Mask_H, Intenisity, Blur)
            masks.append(mask)
                
        if True == Bottom_R:
            mask = create_mask_with_canvas(C_Width, C_Height, C_Width - Mask_W - EdgeToEdge, C_Height - Mask_H - EdgeToEdge, Mask_W, Mask_H, Intenisity, Blur)
            masks.append(mask)
            
        if len(masks) > 0:
            final_mask = combine_mask(masks)
        else:
            final_mask = create_mask_with_canvas(C_Width, C_Height, 0, 0, C_Width, C_Height, Intenisity, Blur)
                                                       
        return (final_mask,)

class CreateCircleMask:
    '''
    ***Used to thought that would be fun, but it doesn't works well, let me know if you create something fun with it***
    
    Create Circle Mask   
    `Intenisity` and `Blur` are not working properly....
        
    Inputs:
    Width, Height       - Canvas size.
            
    Optional Input:
    ***You need connect at least ONE of them***
    opt_circle          - A custom circle information to overrive current settings.            
    circles_provider    - Connect from `Circles Random Generator`
    
    Outputs:
    PngImage            - Preview Image
    Mask                - The Mask
    '''
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "optional": {
                "opt_circle": ("CIRCLE_LIST", {
                    "display": "input" 
                }),      
                "circles_provider": ("CIRCLES_LIST", {
                    "display": "input" 
                }),                             
            },
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
        
    RETURN_TYPES = ('IMAGE', 'MASK', 'STRING',)
    RETURN_NAMES = ('PngImage', 'Mask','Debug',)
    FUNCTION = "CreateCircleMaskEx"
    CATEGORY = cat
    
    def CreateCircleMaskEx(self, Width, Height, circles_provider = None, opt_circle = None):
        if None is not opt_circle:
            circles_provider = opt_circle
        
        if None is circles_provider and None is opt_circle:
            print('***Mira: [Create Circle Mask] -> Connect at least ONE opt node.')
            return (None, None, "Mira:Connect at least ONE opt node")
            
        RGB = (255,0,255)
        PngImage = Image.new("RGBA", [Width, Height])
        PngDraw = ImageDraw.Draw(PngImage)
        PngDraw.rectangle([0, 0, Width, Height], fill=(0, 0, 0))
        DebugMessage = 'Mira:\n'
            
        circle_count = len(circles_provider)
        DebugMessage += 'circle_count = ' + str(circle_count) + '\n'

        for circle in circles_provider:
            X = circle[0]
            Y = circle[1]
            diameter = circle[2]
            dount = circle[3]
            dount_size = circle[4]
            
            DebugMessage += 'Draw [' + str(X) + ',' +  str(Y) + ',' +  str(diameter) + ',' + str(dount) + ',' + str(dount_size) + ']\n'
            PngDraw.ellipse((X, Y, X + diameter, Y + diameter), fill=(RGB))
            if True is dount:
                dount_diameter = math.floor(diameter * dount_size)
                half_dount_diameter = math.floor(dount_diameter / 2)
                half_diameter = math.floor(diameter / 2)
                
                DebugMessage += 'Draw dount [' + str(X + half_diameter - half_dount_diameter) + ',' +  str(Y + half_diameter - half_dount_diameter) + ',' +  str(dount_diameter) + ']\n'
                PngDraw.ellipse((X + half_diameter - half_dount_diameter, Y + half_diameter - half_dount_diameter, X + half_diameter + half_dount_diameter, Y + half_diameter + half_dount_diameter), fill=(0, 0, 0))
                                
        output_image = LoadImagePNG(PngImage)   

        # ComfyUI ImageColorToMask
        temp = (torch.clamp(output_image, 0, 1.0) * 255.0).round().to(torch.int)
        temp = torch.bitwise_left_shift(temp[:,:,:,0], 16) + torch.bitwise_left_shift(temp[:,:,:,1], 8) + temp[:,:,:,2]
        final_mask = torch.where(temp == (255<<16|0<<8|255), 255, 0).float()    
                        
        return (output_image, final_mask, DebugMessage,)
    
    