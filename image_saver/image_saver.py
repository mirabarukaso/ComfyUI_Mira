# Forked from https://github.com/alexopus/ComfyUI-Image-Saver
# Remove download from civitai.com and easy remix

import os
from datetime import datetime
from pathlib import Path
import json
from PIL import Image
import numpy as np
import re
import folder_paths
from .saver import save_image
from .utils import get_sha256
from .prompt_metadata_extractor import PromptMetadataExtractor

MAX_RESOLUTION = 16384
cat_image = "Mira/Util/Image"

def parse_checkpoint_name(ckpt_name):
    return os.path.basename(ckpt_name)

def parse_checkpoint_name_without_extension(ckpt_name):
    return os.path.splitext(parse_checkpoint_name(ckpt_name))[0]

def get_timestamp(time_format):
    now = datetime.now()
    try:
        timestamp = now.strftime(time_format)
    except:
        timestamp = now.strftime("%Y-%m-%d-%H%M%S")

    return timestamp

def save_json(image_info, filename):
    try:
        workflow = (image_info or {}).get('workflow')
        if workflow is None:
            print('No image info found, skipping saving of JSON')
        with open(f'{filename}.json', 'w') as workflow_file:
            json.dump(workflow, workflow_file)
            print(f'Saved workflow to {filename}.json')
    except Exception as e:
        print(f'Failed to save workflow as json due to: {e}, proceeding with the remainder of saving execution')

def make_pathname(filename, width, height, seed, modelname, counter, time_format, sampler_name, steps, cfg, scheduler, denoise, clip_skip):
    filename = filename.replace("%date", get_timestamp("%Y-%m-%d"))
    filename = filename.replace("%time", get_timestamp(time_format))
    filename = filename.replace("%model", parse_checkpoint_name(modelname))
    filename = filename.replace("%width", str(width))
    filename = filename.replace("%height", str(height))
    filename = filename.replace("%seed", str(seed))
    filename = filename.replace("%counter", str(counter))
    filename = filename.replace("%sampler_name", sampler_name)
    filename = filename.replace("%steps", str(steps))
    filename = filename.replace("%cfg", str(cfg))
    filename = filename.replace("%scheduler", scheduler)
    filename = filename.replace("%basemodelname", parse_checkpoint_name_without_extension(modelname))
    filename = filename.replace("%denoise", str(denoise))
    filename = filename.replace("%clip_skip", str(clip_skip))
    return filename

def make_filename(filename, width, height, seed, modelname, counter, time_format, sampler_name, steps, cfg, scheduler, denoise, clip_skip):
    filename = make_pathname(filename, width, height, seed, modelname, counter, time_format, sampler_name, steps, cfg, scheduler, denoise, clip_skip)
    return get_timestamp(time_format) if filename == "" else filename

class ImageSaver:
    def __init__(self):
        self.output_dir = folder_paths.output_directory
        self.civitai_sampler_map = {
            'euler_ancestral': 'Euler a',
            'euler': 'Euler',
            'lms': 'LMS',
            'heun': 'Heun',
            'dpm_2': 'DPM2',
            'dpm_2_ancestral': 'DPM2 a',
            'dpmpp_2s_ancestral': 'DPM++ 2S a',
            'dpmpp_2m': 'DPM++ 2M',
            'dpmpp_sde': 'DPM++ SDE',
            'dpmpp_2m_sde': 'DPM++ 2M SDE',
            'dpmpp_3m_sde': 'DPM++ 3M SDE',
            'dpm_fast': 'DPM fast',
            'dpm_adaptive': 'DPM adaptive',
            'ddim': 'DDIM',
            'plms': 'PLMS',
            'uni_pc_bh2': 'UniPC',
            'uni_pc': 'UniPC',
            'lcm': 'LCM',            
        }
        
        self.a1111_schedule_map = {
            "karras": "Karras", 
            "exponential": "Exponential", 
            "sgm_uniform": "SGM Uniform", 
            "kl_optimal": "KL Optimal", 
            "simple": "Simple", 
            "normal": "Normal", 
            "ddim_uniform": "DDIM", 
            "beta": "Beta",
        }

    def get_civitai_sampler_name(self, sampler_name, scheduler):
        # based on: https://github.com/civitai/civitai/blob/main/src/server/common/constants.ts#L122
        if sampler_name in self.civitai_sampler_map:
            civitai_name = self.civitai_sampler_map[sampler_name]

            if scheduler == "karras":
                civitai_name += " Karras"
            elif scheduler == "exponential":
                civitai_name += " Exponential"

            return civitai_name
        else:
            return sampler_name
            
    def get_a1111_schedule_name(self, scheduler_name):
        # based on: https://github.com/civitai/civitai/blob/main/src/server/common/constants.ts#L122
        if scheduler_name in self.a1111_schedule_map:
            a1111_name = self.a1111_schedule_map[scheduler_name]
            return a1111_name
        else:
            return scheduler_name

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images":                ("IMAGE",   {                                                             "tooltip": "image(s) to save"}),
                "filename":              ("STRING",  {"default": '%time_%basemodelname_%seed', "multiline": False, "tooltip": "filename (available variables: %date, %time, %model, %width, %height, %seed, %counter, %sampler_name, %steps, %cfg, %scheduler, %basemodelname, %denoise, %clip_skip)"}),
                "path":                  ("STRING",  {"default": '', "multiline": False,                           "tooltip": "path to save the images (under Comfy's save directory)"}),
                "extension":             (['png', 'jpeg', 'jpg', 'webp'], {                                        "tooltip": "file extension/type to save image as"}),
            },
            "optional": {
                "steps":                 ("INT",     {"default": 20, "min": 1, "max": 10000,                       "tooltip": "number of steps"}),
                "cfg":                   ("FLOAT",   {"default": 7.0, "min": 0.0, "max": 100.0,                    "tooltip": "CFG value"}),
                "modelname":             ("STRING",  {"default": '', "multiline": False,                           "tooltip": "model name"}),
                "sampler_name":          ("STRING",  {"default": '', "multiline": False,                           "tooltip": "sampler name (as string)"}),
                "scheduler":             ("STRING",  {"default": 'normal', "multiline": False,                     "tooltip": "scheduler name (as string)"}),
                "positive":              ("STRING",  {"default": 'unknown', "multiline": True,                     "tooltip": "positive prompt"}),
                "negative":              ("STRING",  {"default": 'unknown', "multiline": True,                     "tooltip": "negative prompt"}),
                "seed_value":            ("INT",     {"default": 0, "min": 0, "max": 0xffffffffffffffff,           "tooltip": "seed"}),
                "width":                 ("INT",     {"default": 512, "min": 0, "max": MAX_RESOLUTION, "step": 8,  "tooltip": "image width"}),
                "height":                ("INT",     {"default": 512, "min": 0, "max": MAX_RESOLUTION, "step": 8,  "tooltip": "image height"}),
                "lossless_webp":         ("BOOLEAN", {"default": True,                                             "tooltip": "if True, saved WEBP files will be lossless"}),
                "quality_jpeg_or_webp":  ("INT",     {"default": 100, "min": 1, "max": 100,                        "tooltip": "quality setting of JPEG/WEBP"}),
                "optimize_png":          ("BOOLEAN", {"default": False,                                            "tooltip": "if True, saved PNG files will be optimized (can reduce file size but is slower)"}),
                "counter":               ("INT",     {"default": 0, "min": 0, "max": 0xffffffffffffffff,           "tooltip": "counter"}),
                "denoise":               ("FLOAT",   {"default": 1.0, "min": 0.0, "max": 1.0,                      "tooltip": "denoise value"}),
                "clip_skip":             ("INT",     {"default": 0, "min": -24, "max": 24,                         "tooltip": "skip last CLIP layers (positive or negative value, 0 for no skip)"}),
                "time_format":           ("STRING",  {"default": "%Y-%m-%d-%H%M%S", "multiline": False,            "tooltip": "timestamp format"}),
                "save_workflow_as_json": ("BOOLEAN", {"default": False,                                            "tooltip": "if True, also saves the workflow as a separate JSON file"}),
                "embed_workflow":        ("BOOLEAN", {"default": True,                                             "tooltip": "if True, embeds the workflow in the saved image files.\nStable for PNG, experimental for WEBP.\nJPEG experimental and only if metadata size is below 65535 bytes"}),
                "additional_hashes":     ("STRING",  {"default": "", "multiline": False,                           "tooltip": "hashes separated by commas, optionally with names. 'Name:HASH' (e.g., 'MyLoRA:FF735FF83F98')"}),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("hashes",)
    OUTPUT_TOOLTIPS = ("Comma-separated list of the hashes to chain with other Image Saver additional_hashes",)
    FUNCTION = "save_files"

    OUTPUT_NODE = True

    CATEGORY = cat_image
    DESCRIPTION = "Save images with generation metadata"

    # Match 'anything' or 'anything:anything' with trimmed white space
    re_manual_hash = re.compile(r'^\s*([^:]+?)(?:\s*:\s*([^\s:][^:]*?))?\s*$')
    MAX_HASH_LENGTH = 16 # skip larger unshortened hashes, such as full sha256 or blake3

    def save_files(
        self,
        images,
        seed_value,
        steps,
        cfg,
        sampler_name,
        scheduler,
        positive,
        negative,
        modelname,
        quality_jpeg_or_webp,
        lossless_webp,
        optimize_png,
        width,
        height,
        counter,
        filename,
        path,
        extension,
        time_format,
        denoise,
        clip_skip,
        additional_hashes="",
        save_workflow_as_json=False,
        embed_workflow=True,
        prompt=None,
        extra_pnginfo=None,
    ):
        filename = make_filename(filename, width, height, seed_value, modelname, counter, time_format, sampler_name, steps, cfg, scheduler, denoise, clip_skip)
        path = make_pathname(path, width, height, seed_value, modelname, counter, time_format, sampler_name, steps, cfg, scheduler, denoise, clip_skip)
        ckpt_path = folder_paths.get_full_path("checkpoints", modelname)

        if not ckpt_path:
            ckpt_path = folder_paths.get_full_path("diffusion_models", modelname)

        if ckpt_path:
            modelhash = get_sha256(ckpt_path)[:10]
        else:
            modelhash = ""

        metadata_extractor = PromptMetadataExtractor([positive, negative])
        embeddings = metadata_extractor.get_embeddings()
        loras = metadata_extractor.get_loras()
        civitai_sampler_name = self.get_civitai_sampler_name(sampler_name.replace('_gpu', ''), scheduler)

        # Process additional_hashes input (a string) by normalizing, removing extra spaces/newlines, and splitting by comma
        manual_entries = {}
        unnamed_count = 0
        existing_hashes = {modelhash.lower()} | {t[2].lower() for t in loras.values()} | {t[2].lower() for t in embeddings.values()}  # Get set of parsed hashes
        additional_hash_split = additional_hashes.replace("\n", ",").split(",") if additional_hashes else []
        for entry in additional_hash_split:
            match = self.re_manual_hash.search(entry)
            if match is None:
                print(f"ComfyUI-Image-Saver: Invalid additional hash string: '{entry}'")
                continue

            groups = tuple(group for group in match.groups() if group)

            # Read weight and remove from groups, if needed
            weight = None

            # Read hash, optionally preceded by name
            name, hash = groups if len(groups) > 1 else (None, groups[0])

            if len(hash) > self.MAX_HASH_LENGTH:
                print(f"ComfyUI-Image-Saver: Skipping hash. Length exceeds maximum of {self.MAX_HASH_LENGTH} characters: {hash}")
                continue

            if any(hash.lower() == existing_hash.lower() for _, _, existing_hash in manual_entries.values()):
                print(f"ComfyUI-Image-Saver: Skipping duplicate hash: {hash}")
                continue  # Skip duplicates

            if hash.lower() in existing_hashes:
                print(f"ComfyUI-Image-Saver: Skipping manual hash already present in resources: {hash}")
                continue

            if name is None:
                unnamed_count += 1
                name = f"manual{unnamed_count}"
            elif name in manual_entries:
                print(f"ComfyUI-Image-Saver: Duplicate manual hash name '{name}' is being overwritten.")

            manual_entries[name] = (None, weight, hash)

            if len(manual_entries) > 29:
                print("ComfyUI-Image-Saver: Reached maximum limit of 30 manual hashes. Skipping the rest.")
                break

        hashes = {}
        add_model_hash = None
        hashes = {key: value[2] for key, value in embeddings.items()} | {key: value[2] for key, value in loras.items()} | {key: value[2] for key, value in manual_entries.items()} | {"model": modelhash}
        add_model_hash = modelhash
        basemodelname = parse_checkpoint_name_without_extension(modelname)

        positive_a111_params = positive.strip()
        negative_a111_params = f"\nNegative prompt: {negative.strip()}"
        clip_skip_str = f", Clip skip: {abs(clip_skip)}" if clip_skip != 0 else ""
        model_hash_str = f", Model hash: {add_model_hash}" if add_model_hash else ""
        hashes_str = f", Hashes: {json.dumps(hashes, separators=(',', ':'))}" if hashes else ""

        a111_params = (
            f"{positive_a111_params}{negative_a111_params}\n"
            f"Steps: {steps}, Sampler: {civitai_sampler_name}, Schedule type: {self.get_a1111_schedule_name(scheduler)}, CFG scale: {cfg}, Seed: {seed_value}, "
            f"Size: {width}x{height}{clip_skip_str}{model_hash_str}, Model: {basemodelname}{hashes_str}, Version: ComfyUI"
        )

        output_path = os.path.join(self.output_dir, path)

        if output_path.strip() != '' and not os.path.exists(output_path.strip()):
            print(f'The path `{output_path.strip()}` specified doesn\'t exist! Creating directory.')
            os.makedirs(output_path, exist_ok=True)

        filenames = self.save_images(images, output_path, filename, a111_params, extension, quality_jpeg_or_webp, lossless_webp, optimize_png, prompt, extra_pnginfo, save_workflow_as_json, embed_workflow)

        subfolder = os.path.normpath(path)

        return {
            "result": (",".join(f"{Path(name.split(':')[-1]).stem + ':' if name else ''}{hash}{':' + str(weight) if weight is not None else ''}" for name, (_, weight, hash) in ({ modelname: ( ckpt_path, None, modelhash ) } | loras | embeddings | manual_entries).items()),),
            "ui": {"images": map(lambda filename: {"filename": filename, "subfolder": subfolder if subfolder != '.' else '', "type": 'output'}, filenames)},
        }

    def save_images(self, images, output_path, filename_prefix, a111_params, extension, quality_jpeg_or_webp, lossless_webp, optimize_png, prompt, extra_pnginfo, save_workflow_as_json, embed_workflow) -> list[str]:
        paths = list()
        for image in images:
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

            current_filename_prefix = self.get_unique_filename(output_path, filename_prefix, extension)
            filename = f"{current_filename_prefix}.{extension}"
            filepath = os.path.join(output_path, filename)

            save_image(img, filepath, extension, quality_jpeg_or_webp, lossless_webp, optimize_png, a111_params, prompt, extra_pnginfo, embed_workflow)

            if save_workflow_as_json:
                save_json(extra_pnginfo, os.path.join(output_path, current_filename_prefix))

            paths.append(filename)
        return paths

    def get_unique_filename(self, output_path, filename_prefix, extension):
        existing_files = [f for f in os.listdir(output_path) if f.startswith(filename_prefix) and f.endswith(extension)]

        if not existing_files:
            return f"{filename_prefix}"

        suffixes = []
        for f in existing_files:
            name, _ = os.path.splitext(f)
            parts = name.split('_')
            if parts[-1].isdigit():
                suffixes.append(int(parts[-1]))

        if suffixes:
            next_suffix = max(suffixes) + 1
        else:
            next_suffix = 1

        return f"{filename_prefix}_{next_suffix:02d}"

