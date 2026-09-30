"""Build a ComfyUI V3 schema from a V1 INPUT_TYPES dictionary.

Input names, the order inside required, and the order inside optional stay as
they were. ``display: "input"`` is kept as a widget option. It is not converted
to forceInput, because that would drop the widget and break saved workflows.
"""

from comfy_api.latest import IO

DISPLAY = {
    "IntMultiplication": "Integer Multiplication",
    "IntToFloatMultiplication": "Integer to Float Multiplication",
    "FloatMultiplication": "Float Multiplication",
    "IntSubtraction": "Integer Subtraction",
    "NumeralToString": "Convert Numeral to String",
    "OneFloat": "1 Float",
    "TwoFloats": "2 Floats",
    "FourFloats": "4 Floats",
    "EightFloats": "8 Floats",
    "FloatListInterpreter1": "1 Float from List",
    "FloatListInterpreter4": "4 Floats from List",
    "FloatListInterpreter8": "8 Floats from List",
    "StepsAndCfg": "Steps & Cfg",
    "CanvasCreatorAdvanced": "Create Canvas Advanced",
    "CanvasCreatorSimple": "Create Canvas",
    "CanvasCreatorBasic": "Create Canvas H/W only",
    "RandomTillingLayouts": "Random Tilling Layouts",
    "RandomNestedLayouts": "Random Nested Layouts",
    "SeedGeneratorMira": "Random Seed Generator",
    "ImageGrayscale": "To Grayscale",
    "ImageContrast": "Adjust Contrast",
    "ImageSharpness": "Adjust Sharpness",
    "ImageBrightness": "Adjust Brightness",
    "ImageSaturation": "Adjust Saturation",
    "ImageHUE": "Adjust HUE",
    "ImageGamma": "Adjust Gamma",
    "ImageToneCurve": "Tone Curve",
    "ImageColorTransferMira": "Color Transfer",
    "ImageRGBChannel": "RGB Channel",
    "UpscaleImageByModelThenResize": "Upscale Image By Model Then Resize",
    "CheckpointLoaderSimpleMira": "Checkpoint Loader with Name",
    "GzippedBase64ToImage": "Gzipped Base64 To Image",
    "ImageToGzippedBase64": "Image To Gzipped Base64",
    "ReverseImageAndAllImages": "Reverse Images And All Images",
    "StackImages": "Stack Images",
    "FlatColorQuantization": "Flat Color Quantization",
    "CreateTillingPNGMask": "Create Tilling PNG Mask",
    "CreateNestedPNGMask": "Create Nested PNG Mask",
    "CreateSimpleMask": "Create Simple Mask",
    "PngColorMasksToString": "PngColor Mask to HEX String",
    "PngColorMasksToRGB": "PngColor Mask to INT RGB",
    "PngColorMasksToStringList": "PngColor Masks to List",
    "PngColorMasksToMaskList": "PngColor Masks to Masks",
    "PngRectanglesToMask": "PngRectangles to Mask",
    "PngRectanglesToMaskList": "PngRectangles to Masks",
    "CreateMaskWithCanvas": "Create Mask With Canvas",
    "CreateWatermarkRemovalMask": "Create Watermark Removal Mask",
    "SingleBooleanTrigger": "1 Bool",
    "TwoBooleanTrigger": "2 Bools",
    "FourBooleanTrigger": "4 Bools",
    "SixBooleanTrigger": "6 Bools",
    "EightBooleanTrigger": "8 Bools",
    "LogicNot": "Not",
    "EvenOrOdd": "Even or Odd",
    "EvenOrOddList": "Even or Odd List",
    "BooleanListInterpreter1": "1 Bool from List",
    "BooleanListInterpreter4": "4 Bools from List",
    "BooleanListInterpreter8": "8 Bools from List",
    "FunctionSwap": "Function Swap",
    "FunctionSelectAuto": "Function Select Auto",
    "NoneToZero": "None To 0",
    "SN74LVC1G125": "SN74LVC1G125",
    "SN74HC1G86": "SN74HC1G86",
    "SN74HC86": "SN74HC86",
    "TextBoxMira": "Text Box",
    "TextWithBooleanSwitchAndCommonTextInput": "Text Switcher",
    "TextCombinerSix": "Text Combiner 6",
    "TextCombinerTwo": "Text Combiner 2",
    "TextSwitcherTwoWays": "Text Switcher Two Ways",
    "TextSwitcherThreeWays": "Text Switcher Three Ways",
    "TextLoopCombiner": "Text Loop Combiner",
    "TextWildcardSeprator": "Text Wildcard Seprator",
    "LoRALoaderWithNameStacker": "LoRA Loader With Name Stacker",
    "LoRAfromText": "LoRA Loader from Text",
    "llm_prompt_gen_node": "AI Prompt Generator",
    "local_llm_prompt_gen": "Local AI Prompt Generator (llama.cpp)",
    "illustrious_character_select": "WAI illustrious Character Select CN",
    "illustrious_character_select_en": "WAI illustrious Character Select EN",
    "ImageSaverMira": "Image Saver",
    "cl_tagger_mira": "CL Tagger",
    "camie_tagger_mira": "Camie Tagger",
    "wd_tagger_mira": "WD Tagger",
}

_WIDGETS = {
    "INT": IO.Int,
    "FLOAT": IO.Float,
    "STRING": IO.String,
    "BOOLEAN": IO.Boolean,
}

_SOCKETS = {
    "IMAGE": IO.Image,
    "MASK": IO.Mask,
    "MODEL": IO.Model,
    "CLIP": IO.Clip,
    "VAE": IO.Vae,
    "CONDITIONING": IO.Conditioning,
    "LATENT": IO.Latent,
    "UPSCALE_MODEL": IO.UpscaleModel,
}


def _type_name(io_type) -> str:
    if isinstance(io_type, str):
        return str(io_type)
    raise TypeError(f"Unsupported io type {io_type!r}")


def _io_class(io_type: str):
    if io_type == "*":
        return IO.AnyType
    found = _WIDGETS.get(io_type)
    if found is not None:
        return found
    found = _SOCKETS.get(io_type)
    if found is not None:
        return found
    return IO.Custom(io_type)


def _split_display(opts: dict):
    display = opts.pop("display", None)
    if display == "number":
        return IO.NumberDisplay.number, None
    if display == "slider":
        return IO.NumberDisplay.slider, None
    return None, display


def _make_input(name: str, spec, optional: bool):
    if not isinstance(spec, (tuple, list)):
        raise TypeError(f"Input {name!r} spec must be a tuple, got {spec!r}")
    io_type = spec[0]
    opts = dict(spec[1]) if len(spec) > 1 and spec[1] else {}
    tooltip = opts.pop("tooltip", None)

    if isinstance(io_type, (list, tuple)) and not isinstance(io_type, str):
        default = opts.pop("default", None)
        extra = opts or None
        return IO.Combo.Input(
            name,
            options=list(io_type),
            optional=optional,
            tooltip=tooltip,
            default=default,
            extra_dict=extra,
        )

    type_name = _type_name(io_type)
    cls = _io_class(type_name)

    if cls in (IO.Int, IO.Float):
        display_mode, display_extra = _split_display(opts)
        kwargs = {}
        for key in ("default", "min", "max", "step", "round"):
            if key in opts:
                kwargs[key] = opts.pop(key)
        if display_extra is not None:
            opts["display"] = display_extra
        return cls.Input(
            name,
            optional=optional,
            tooltip=tooltip,
            display_mode=display_mode,
            extra_dict=opts or None,
            **kwargs,
        )

    if cls is IO.String:
        _, display_extra = _split_display(opts)
        kwargs = {}
        if "default" in opts:
            kwargs["default"] = opts.pop("default")
        multiline_set = "multiline" in opts
        if multiline_set:
            kwargs["multiline"] = opts.pop("multiline")
        if "placeholder" in opts:
            kwargs["placeholder"] = opts.pop("placeholder")
        if "dynamicPrompts" in opts:
            kwargs["dynamic_prompts"] = opts.pop("dynamicPrompts")
        if display_extra is not None:
            opts["display"] = display_extra
        made = IO.String.Input(
            name,
            optional=optional,
            tooltip=tooltip,
            extra_dict=opts or None,
            **kwargs,
        )
        if not multiline_set:
            made.multiline = None
        return made

    if cls is IO.Boolean:
        _, display_extra = _split_display(opts)
        kwargs = {}
        for key in ("default", "label_on", "label_off"):
            if key in opts:
                kwargs[key] = opts.pop(key)
        if display_extra is not None:
            opts["display"] = display_extra
        return IO.Boolean.Input(
            name,
            optional=optional,
            tooltip=tooltip,
            extra_dict=opts or None,
            **kwargs,
        )

    cleaned = {}
    for key, value in opts.items():
        if key == "default" and value is None:
            continue
        cleaned[key] = value
    return cls.Input(name, optional=optional, tooltip=tooltip, extra_dict=cleaned or None)


def _make_output(io_type, name, tooltip):
    cls = _io_class(_type_name(io_type))
    if tooltip:
        return cls.Output(display_name=name, tooltip=tooltip)
    return cls.Output(display_name=name)


def node(
    node_id: str,
    category: str,
    inputs: dict,
    return_types,
    return_names,
    *,
    description: str = "",
    output_tooltips=None,
    is_output_node: bool = False,
    hidden=None,
) -> IO.Schema:
    """Create a schema whose V1 projection matches the historical node."""
    display_name = DISPLAY[node_id]
    made = []
    for section in ("required", "optional"):
        block = inputs.get(section) or {}
        optional = section == "optional"
        for name, spec in block.items():
            made.append(_make_input(name, spec, optional))

    types = tuple(return_types)
    names = tuple(return_names)
    if len(types) != len(names):
        raise ValueError(f"{node_id} has {len(types)} return types and {len(names)} return names")
    tips = tuple(output_tooltips or ())
    outputs = []
    for index, (io_type, name) in enumerate(zip(types, names)):
        tip = tips[index] if index < len(tips) else None
        outputs.append(_make_output(io_type, name, tip))

    return IO.Schema(
        node_id=node_id,
        display_name=display_name,
        category=category,
        inputs=made,
        outputs=outputs,
        hidden=list(hidden or []),
        description=description or "",
        is_output_node=is_output_node,
    )
