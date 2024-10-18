from .Arithmetic import IntMultiplication, IntToFloatMultiplication, FloatMultiplication, IntSubtraction
from .Numeral import NumeralToString, OneFloat, TwoFloats, FourFloats, EightFloats, FloatListInterpreter1, FloatListInterpreter4, FloatListInterpreter8, StepsAndCfg
from .Util import CanvasCreatorAdvanced, CanvasCreatorSimple, CanvasCreatorBasic, RandomTillingLayouts, RandomNestedLayouts, SeedGenerator
from .Util import ImageGrayscale, ImageContrast, ImageSharpness, ImageBrightness, ImageSaturation, ImageHUE, ImageGamma, ImageColorTransfer
from .Mask import CreateTillingPNGMask, CreateNestedPNGMask, PngColorMasksToString, PngColorMasksToRGB, PngColorMasksToStringList, PngColorMasksToMaskList, PngRectanglesToMask, PngRectanglesToMaskList, CreateMaskWithCanvas, CreateWatermarkRemovalMask, CreateSimpleMask
from .Text import TextBox, TextWithBooleanSwitchAndCommonTextInput, TextCombinerSix, TextCombinerTwo, TextSwitcherTwoWays, TextSwitcherThreeWays
from .Logic import SingleBooleanTrigger, TwoBooleanTrigger, FourBooleanTrigger, SixBooleanTrigger, EightBooleanTrigger, LogicNot, EvenOrOdd, EvenOrOddList, BooleanListInterpreter1, BooleanListInterpreter4, BooleanListInterpreter8, FunctionSwap, NoneToZero
from .Logic import SN74LVC1G125, SN74HC1G86, SN74HC86
from .Lora import LoRALoaderWithNameStacker
def __init__(self):
    pass
    
# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "IntMultiplication"         : IntMultiplication,
    "IntToFloatMultiplication"  : IntToFloatMultiplication,
    "FloatMultiplication"       : FloatMultiplication,
    "IntSubtraction"            : IntSubtraction,
    
    "NumeralToString"           : NumeralToString,
    "OneFloat"                  : OneFloat,
    "TwoFloats"                 : TwoFloats,
    "FourFloats"                : FourFloats,
    "EightFloats"               : EightFloats,    
    "FloatListInterpreter1"     : FloatListInterpreter1,
    "FloatListInterpreter4"     : FloatListInterpreter4,
    "FloatListInterpreter8"     : FloatListInterpreter8,
    "StepsAndCfg"               : StepsAndCfg,
        
    "CanvasCreatorAdvanced"     : CanvasCreatorAdvanced,
    "CanvasCreatorSimple"       : CanvasCreatorSimple,
    "CanvasCreatorBasic"        : CanvasCreatorBasic,
    "RandomTillingLayouts"      : RandomTillingLayouts,
    "RandomNestedLayouts"       : RandomNestedLayouts,
    "SeedGenerator"             : SeedGenerator,
    
    "ImageGrayscale"            : ImageGrayscale,
    "ImageContrast"             : ImageContrast,
    "ImageSharpness"            : ImageSharpness,
    "ImageBrightness"           : ImageBrightness,
    "ImageSaturation"           : ImageSaturation,
    "ImageHUE"                  : ImageHUE,
    "ImageGamma"                : ImageGamma,
    "ImageColorTransfer"        : ImageColorTransfer,

    "CreateTillingPNGMask"      : CreateTillingPNGMask,
    "CreateNestedPNGMask"       : CreateNestedPNGMask,
    "CreateSimpleMask"          : CreateSimpleMask,
    "PngColorMasksToString"     : PngColorMasksToString,
    "PngColorMasksToRGB"        : PngColorMasksToRGB,
    "PngColorMasksToStringList" : PngColorMasksToStringList,
    "PngColorMasksToMaskList"   : PngColorMasksToMaskList,
    "PngRectanglesToMask"       : PngRectanglesToMask,
    "PngRectanglesToMaskList"   : PngRectanglesToMaskList,
    "CreateMaskWithCanvas"      : CreateMaskWithCanvas,
    "CreateWatermarkRemovalMask": CreateWatermarkRemovalMask,
    
    "SingleBooleanTrigger"      : SingleBooleanTrigger,
    "TwoBooleanTrigger"         : TwoBooleanTrigger,
    "FourBooleanTrigger"        : FourBooleanTrigger,
    "SixBooleanTrigger"         : SixBooleanTrigger,
    "EightBooleanTrigger"       : EightBooleanTrigger,
    "LogicNot"                  : LogicNot,
    "EvenOrOdd"                 : EvenOrOdd,
    "EvenOrOddList"             : EvenOrOddList,
    "BooleanListInterpreter1"   : BooleanListInterpreter1,
    "BooleanListInterpreter4"   : BooleanListInterpreter4,
    "BooleanListInterpreter8"   : BooleanListInterpreter8,
    "FunctionSwap"              : FunctionSwap,
    "NoneToZero"                : NoneToZero,
    
    "SN74LVC1G125"              : SN74LVC1G125,
    "SN74HC1G86"                : SN74HC1G86,
    "SN74HC86"                  : SN74HC86,
    
    "TextBox"                                   : TextBox,
    "TextWithBooleanSwitchAndCommonTextInput"   : TextWithBooleanSwitchAndCommonTextInput,
    "TextCombinerSix"                           : TextCombinerSix,
    "TextCombinerTwo"                           : TextCombinerTwo,
    "TextSwitcherTwoWays"                       : TextSwitcherTwoWays,
    "TextSwitcherThreeWays"                     : TextSwitcherThreeWays,
    
    "LoRALoaderWithNameStacker" : LoRALoaderWithNameStacker,
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "IntMultiplication"         : "Integer Multiplication",
    "IntToFloatMultiplication"  : "Integer to Float Multiplication",
    "FloatMultiplication"       : "Float Multiplication",
    "IntSubtraction"            : "Integer Subtraction",
    
    "NumeralToString"           : "Convert Numeral to String",
    "OneFloat"                  : "1 Float",
    "TwoFloats"                 : "2 Floats",
    "FourFloats"                : "4 Floats",
    "EightFloats"               : "8 Floats",
    "FloatListInterpreter1"     : "1 Float from List",
    "FloatListInterpreter4"     : "4 Floats from List",
    "FloatListInterpreter8"     : "8 Floats from List",
    "StepsAndCfg"               : "Steps & Cfg",
    
    "CanvasCreatorAdvanced"     : "Create Canvas Advanced",
    "CanvasCreatorSimple"       : "Create Canvas",
    "CanvasCreatorBasic"        : "Create Canvas H/W only",
    "RandomTillingLayouts"      : "Random Tilling Layouts",
    "RandomNestedLayouts"       : "Random Nested Layouts",
    "SeedGenerator"             : "Random Seed Generator",
    
    "ImageGrayscale"            : "To Grayscale",
    "ImageContrast"             : "Adjust Contrast",
    "ImageSharpness"            : "Adjust Sharpness",
    "ImageBrightness"           : "Adjust Brightness",
    "ImageSaturation"           : "Adjust Saturation",
    "ImageHUE"                  : "Adjust HUE",
    "ImageGamma"                : "Adjust Gamma",
    "ImageColorTransfer"        : "Color Transfer",
    
    "CreateTillingPNGMask"      : "Create Tilling PNG Mask",
    "CreateNestedPNGMask"       : "Create Nested PNG Mask",
    "CreateSimpleMask"          : "Create Simple Mask",
    "PngColorMasksToString"     : "PngColor Mask to HEX String",
    "PngColorMasksToRGB"        : "PngColor Mask to INT RGB",
    "PngColorMasksToStringList" : "PngColor Masks to List",
    "PngColorMasksToMaskList"   : "PngColor Masks to Masks",
    "PngRectanglesToMask"       : "PngRectangles to Mask",
    "PngRectanglesToMaskList"   : "PngRectangles to Masks",
    "CreateMaskWithCanvas"      : "Create Mask With Canvas",
    "CreateWatermarkRemovalMask": "Create Watermark Removal Mask",
    
    "SingleBooleanTrigger"      : "1 Bool",
    "TwoBooleanTrigger"         : "2 Bools",
    "FourBooleanTrigger"        : "4 Bools",
    "SixBooleanTrigger"         : "6 Bools",
    "EightBooleanTrigger"       : "8 Bools",
    "LogicNot"                  : "Not",
    "EvenOrOdd"                 : "Even or Odd",
    "EvenOrOddList"             : "Even or Odd List",
    "BooleanListInterpreter1"   : "1 Bool from List",
    "BooleanListInterpreter4"   : "4 Bools from List",
    "BooleanListInterpreter8"   : "8 Bools from List",
    "FunctionSwap"              : "Function Swap",
    "NoneToZero"                : "None To 0",
    
    "SN74LVC1G125"              : "SN74LVC1G125",
    "SN74HC1G86"                : "SN74HC1G86",
    "SN74HC86"                  : "SN74HC86",
    
    "TextBox"                                   : "Text Box",
    "TextWithBooleanSwitchAndCommonTextInput"   : "Text Switcher",
    "TextCombinerSix"                           : "Text Combiner 6",
    "TextCombinerTwo"                           : "Text Combiner 2",
    "TextSwitcherTwoWays"                       : "Text Switcher Two Ways",
    "TextSwitcherThreeWays"                     : "Text Switcher Three Ways",
    
    "LoRALoaderWithNameStacker" : "LoRA Loader With Name Stacker",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

