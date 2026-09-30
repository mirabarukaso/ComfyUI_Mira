from .Arithmetic import IntMultiplication, IntToFloatMultiplication, FloatMultiplication, IntSubtraction
from .Numeral import NumeralToString, OneFloat, TwoFloats, FourFloats, EightFloats, FloatListInterpreter1, FloatListInterpreter4, FloatListInterpreter8, StepsAndCfg
from .Util import CanvasCreatorAdvanced, CanvasCreatorSimple, CanvasCreatorBasic, RandomTillingLayouts, RandomNestedLayouts, SeedGenerator
from .Util import ImageGrayscale, ImageContrast, ImageSharpness, ImageBrightness, ImageSaturation, ImageHUE, ImageGamma, ImageToneCurve, ImageColorTransfer, ImageRGBChannel, UpscaleImageByModelThenResize
from .Util import CheckpointLoaderSimple, GzippedBase64ToImage, ImageToGzippedBase64, ReverseImageAndAllImages, StackImages, FlatColorQuantization
from .Mask import CreateTillingPNGMask, CreateNestedPNGMask, PngColorMasksToString, PngColorMasksToRGB, PngColorMasksToStringList, PngColorMasksToMaskList, PngRectanglesToMask, PngRectanglesToMaskList, CreateMaskWithCanvas, CreateWatermarkRemovalMask, CreateSimpleMask
from .Text import TextBox, TextWithBooleanSwitchAndCommonTextInput, TextCombinerSix, TextCombinerTwo, TextSwitcherTwoWays, TextSwitcherThreeWays, TextLoopCombiner, TextWildcardSeprator
from .Logic import SingleBooleanTrigger, TwoBooleanTrigger, FourBooleanTrigger, SixBooleanTrigger, EightBooleanTrigger, LogicNot, EvenOrOdd, EvenOrOddList, BooleanListInterpreter1, BooleanListInterpreter4, BooleanListInterpreter8, FunctionSwap, FunctionSelectAuto, NoneToZero
from .Logic import SN74LVC1G125, SN74HC1G86, SN74HC86
from .Lora import LoRALoaderWithNameStacker, LoRAfromText
from .Tagger import cl_tagger, camie_tagger, wd_tagger
from .wai_illustrious_character_select import llm_prompt_gen_node, illustrious_character_select, illustrious_character_select_en, local_llm_prompt_gen
from .image_saver.image_saver import ImageSaver
from comfy_api.latest import ComfyExtension

class MiraExtension(ComfyExtension):
    async def get_node_list(self):
        return [
            IntMultiplication,
            IntToFloatMultiplication,
            FloatMultiplication,
            IntSubtraction,
            NumeralToString,
            OneFloat,
            TwoFloats,
            FourFloats,
            EightFloats,
            FloatListInterpreter1,
            FloatListInterpreter4,
            FloatListInterpreter8,
            StepsAndCfg,
            CanvasCreatorAdvanced,
            CanvasCreatorSimple,
            CanvasCreatorBasic,
            RandomTillingLayouts,
            RandomNestedLayouts,
            SeedGenerator,
            ImageGrayscale,
            ImageContrast,
            ImageSharpness,
            ImageBrightness,
            ImageSaturation,
            ImageHUE,
            ImageGamma,
            ImageToneCurve,
            ImageColorTransfer,
            ImageRGBChannel,
            UpscaleImageByModelThenResize,
            CheckpointLoaderSimple,
            GzippedBase64ToImage,
            ImageToGzippedBase64,
            ReverseImageAndAllImages,
            StackImages,
            FlatColorQuantization,
            CreateTillingPNGMask,
            CreateNestedPNGMask,
            CreateSimpleMask,
            PngColorMasksToString,
            PngColorMasksToRGB,
            PngColorMasksToStringList,
            PngColorMasksToMaskList,
            PngRectanglesToMask,
            PngRectanglesToMaskList,
            CreateMaskWithCanvas,
            CreateWatermarkRemovalMask,
            SingleBooleanTrigger,
            TwoBooleanTrigger,
            FourBooleanTrigger,
            SixBooleanTrigger,
            EightBooleanTrigger,
            LogicNot,
            EvenOrOdd,
            EvenOrOddList,
            BooleanListInterpreter1,
            BooleanListInterpreter4,
            BooleanListInterpreter8,
            FunctionSwap,
            FunctionSelectAuto,
            NoneToZero,
            SN74LVC1G125,
            SN74HC1G86,
            SN74HC86,
            TextBox,
            TextWithBooleanSwitchAndCommonTextInput,
            TextCombinerSix,
            TextCombinerTwo,
            TextSwitcherTwoWays,
            TextSwitcherThreeWays,
            TextLoopCombiner,
            TextWildcardSeprator,
            LoRALoaderWithNameStacker,
            LoRAfromText,
            llm_prompt_gen_node,
            illustrious_character_select,
            illustrious_character_select_en,
            local_llm_prompt_gen,
            ImageSaver,
            cl_tagger,
            camie_tagger,
            wd_tagger,
        ]

async def comfy_entrypoint():
    return MiraExtension()

__all__ = ["comfy_entrypoint"]
