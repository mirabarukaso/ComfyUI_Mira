from .Multiplier import IntMultiplier, FloatMultiplier
from .Numeral import NumeralToString
from .Util import CanvasCreatorAdvanced, CanvasCreatorSimple, CanvasCreatorBasic
from .Mask import CreateRegionalPNGMask, PngColorMasksToString, PngColorMasksToRGB, PngColorMasksToStringList, PngColorMasksToMaskList, PngRectanglesToMask, PngRectanglesToMaskList

def __init__(self):
    pass
    
# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "IntMultiplier"             : IntMultiplier,
    "FloatMultiplier"           : FloatMultiplier,
    "NumeralToString"           : NumeralToString,
    "CanvasCreatorAdvanced"     : CanvasCreatorAdvanced,
    "CanvasCreatorSimple"       : CanvasCreatorSimple,
    "CanvasCreatorBasic"        : CanvasCreatorBasic,
    "CreateRegionalPNGMask"     : CreateRegionalPNGMask,
    "PngColorMasksToString"     : PngColorMasksToString,
    "PngColorMasksToRGB"        : PngColorMasksToRGB,
    "PngColorMasksToStringList" : PngColorMasksToStringList,
    "PngColorMasksToMaskList"   : PngColorMasksToMaskList,
    "PngRectanglesToMask"       : PngRectanglesToMask,
    "PngRectanglesToMaskList"   : PngRectanglesToMaskList,
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "IntMultiplier"             : "Integer Multiplier",
    "FloatMultiplier"           : "Float Multiplier",
    "NumeralToString"           : "Convert Numeral to String",
    "CanvasCreatorAdvanced"     : "Create Canvas Advanced",
    "CanvasCreatorSimple"       : "Create Canvas",
    "CanvasCreatorBasic"        : "Create Canvas H/W only",
    "CreateRegionalPNGMask"     : "Create PNG Mask",
    "PngColorMasksToString"     : "PngColor Mask to HEX String",
    "PngColorMasksToRGB"        : "PngColor Mask to INT RGB",
    "PngColorMasksToStringList" : "PngColor Masks to List",
    "PngColorMasksToMaskList"   : "PngColor Masks to Mask List",
    "PngRectanglesToMask"       : "PngRectangles to Mask",
    "PngRectanglesToMaskList"   : "PngRectangles to Mask List",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]