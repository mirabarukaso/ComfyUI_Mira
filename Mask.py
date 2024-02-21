from PIL import Image
import random
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageSequence
from PIL.PngImagePlugin import PngInfo
import numpy as np
import torch
import re

cat = "Mira/Mask"

def special_match(strg, search=re.compile(r'[^0-9.,;]').search):
    return not bool(search(strg))
   
def RectWidth(Rectangles, Range, nowWidth, warpWidth, y, Width, Height, WarpTimesArray = None):
    warpTimes = 1.0            
    for i in range(Range):            
        if None is not WarpTimesArray:
            warpTimes = float(WarpTimesArray[i])
        if Width - nowWidth - (warpWidth * warpTimes)<= 8:
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
        if Height - nowHeight - (warpHeight * warpTimes) <= 8:
            Rectangles.append([x, int(nowHeight), Width, Height])    
        else:
            Rectangles.append([x, int(nowHeight), Width, int(nowHeight + (warpHeight * warpTimes))])
        nowHeight = nowHeight + (warpHeight * warpTimes)
    return Rectangles
    
def CreatePNG(Width, Height, Rows, Colums, Colum_first, Layout, DebugMessage):
    DebugMessage += 'Mira:\n'
    Rectangles = []
    BlocksCount = Rows * Colums
    
    nowWidth = 0
    nowHeight = 0
    warpWidth = 0
    warpHeight = 0
    
    # , == seperate row
    # ; == seperate colum, has higher prority to cut masks
    # Colum_first == swap , and ;
    if False == special_match(Layout):
        print('Mira: syntaxerror in layout -> [' + Layout + '] Will use Rows * Colums')
        DebugMessage += 'syntaxerror in layout -> [' + Layout + '] Will use Rows * Colums\n'
        
        new_layout = ''
        for _ in range(Rows):
            new_layout += '1,'
            for _ in range(Colums):
                new_layout += '1,'
            new_layout = new_layout[:-1] + ';'
        new_layout = new_layout[:-1]
        print("Mira: new_layout: " + new_layout)
        DebugMessage += 'new_layout: ' + new_layout + '\n'
        return CreatePNG(Width, Height, Rows, Colums, Colum_first, new_layout, DebugMessage)
    else:        
        print('Mira: use Layouts')
        DebugMessage += 'use Layouts\n'
        isSingleSeparator = False
        
        BlocksCount = 0
        WarpTimesArray = 0
            
        if ',' in Layout and ';' not in Layout:
            print('Mira: only , ')
            BlocksCount = Layout.count(',') + 1
            WarpTimesArray = Layout.split(',')
            isSingleSeparator = True
        elif ';' in Layout and ',' not in Layout:
            print('Mira: only ; ')
            BlocksCount = Layout.count(';') + 1
            WarpTimesArray = Layout.split(';')
            isSingleSeparator = True
        else:            
            print('Mira: both , ;')
            
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
                                        
                    if Height - nowHeightEnd <= 8:
                        nowHeightEnd = Height
                    
                    if 1 >= len(FullWarpTimesArray):
                        print('Mira: By pass empty GreatCuts')                        
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
                                        
                    if Width - nowWidthEnd <= 8:
                        nowWidthEnd = Width
                    
                    if 1 >= len(FullWarpTimesArray):
                        print('Mira: By pass empty GreatCuts')                        
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
            print('Mira: [' + str(i) +']Draw ' + str(Rectangles[i]) + ' with ' + str(PngColorMasks[i]) + hex_rgb + '\n')
            DebugMessage += '[' + str(i) +']Draw ' + str(Rectangles[i]) + ' with ' + str(PngColorMasks[i]) + hex_rgb +'\n'
            PngDraw.rectangle(Rectangles[i], fill=(PngColorMasks[i][0], PngColorMasks[i][1], PngColorMasks[i][2], 255))
        DebugMessage += '\n'
                
        return PngImage, PngColorMasks, DebugMessage

class CreateRegionalMask:
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
                
    RETURN_TYPES = ("IMAGE", "LIST", "STRING",)
    RETURN_NAMES = ("Image", "PngColorMasks", "Debug",)
    FUNCTION = "CreateRegionalMaskEx"
    CATEGORY = cat
    
    def CreateRegionalMaskEx(self, Width, Height, Rows, Colums, Colum_first, Layout = '#'):                                         
        DebugMessage = ''
        PngImage, PngColorMasks, DebugMessage = CreatePNG(Width, Height, Rows, Colums, Colum_first, Layout, DebugMessage)
        
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
            
        return (output_image, PngColorMasks, DebugMessage,)
    
class ColorMasksToString:
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
    
class ColorMasksToRGB:
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
    
class ColorMasksToStringList:
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