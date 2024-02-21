from .Multiplier import IntMultiplier, FloatMultiplier
from .Numeral import NumeralToString
from .Util import CanvasCreatorAdvanced, CanvasCreatorSimple
from .Mask import CreateRegionalMask, ColorMasksToString, ColorMasksToRGB, ColorMasksToStringList

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
    "CreateRegionalMask"        : CreateRegionalMask,
    "ColorMasksToString"        : ColorMasksToString,
    "ColorMasksToRGB"           : ColorMasksToRGB,
    "ColorMasksToStringList"    : ColorMasksToStringList,
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "IntMultiplier"             : "Integer Multiplier",
    "FloatMultiplier"           : "Float Multiplier",
    "NumeralToString"           : "Convert Numeral to String",
    "CanvasCreatorAdvanced"     : "Create Canvas Advanced",
    "CanvasCreatorSimple"       : "Create Canvas",
    "CreateRegionalMask"        : "Create PNG Mask",
    "ColorMasksToString"        : "Color Mask to HEX String",
    "ColorMasksToRGB"           : "Color Mask to INT RGB",
    "ColorMasksToStringList"    : "Color Masks to List",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]