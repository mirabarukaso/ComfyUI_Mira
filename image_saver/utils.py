import os
from pathlib import Path
import hashlib
from tqdm import tqdm
import folder_paths

"""
Given the file path, finds a matching sha256 file, or creates one
based on the headers in the source file
"""
def get_sha256(file_path: str):
    file_no_ext = os.path.splitext(file_path)[0]
    hash_file = file_no_ext + ".sha256"

    if os.path.exists(hash_file):
        try:
            with open(hash_file, "r") as f:
                return f.read().strip()
        except OSError as e:
            print(f"ComfyUI-Image-Saver: Error reading existing hash file: {e}")

    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        file_size = os.fstat(f.fileno()).st_size
        block_size = 1048576 # 1 MB

        print(f"ComfyUI-Image-Saver: Calculating sha256 for '{Path(file_path).stem}'")
        with tqdm(None, None, file_size, unit="B", unit_scale=True, unit_divisor=1024) as progress_bar:
            for byte_block in iter(lambda: f.read(block_size), b""):
                progress_bar.update(len(byte_block))
                sha256_hash.update(byte_block)

    try:
        with open(hash_file, "w") as f:
            f.write(sha256_hash.hexdigest())
    except OSError as e:
        print(f"ComfyUI-Image-Saver: Error writing hash to {hash_file}: {e}")

    return sha256_hash.hexdigest()

"""
Represent the given embedding name as key as detected by civitAI
"""
def civitai_embedding_key_name(embedding: str):
    return f'embed:{embedding}'

"""
Represent the given lora name as key as detected by civitAI
NB: this should also work fine for Lycoris
"""
def civitai_lora_key_name(lora: str):
    return f'LORA:{lora}'

"""
Based on a embedding name, eg: EasyNegative, finds the path as known in comfy, including extension
"""
def full_embedding_path_for(embedding: str):
    matching_embedding = next((x for x in __list_embeddings() if x.startswith(embedding)), None)
    if matching_embedding == None:
        return None
    return folder_paths.get_full_path("embeddings", matching_embedding)

"""
Based on a lora name, e.g., 'epi_noise_offset2', finds the path as known in comfy, including extension.
"""
def full_lora_path_for(lora: str):
    # Find the position of the last dot
    last_dot_position = lora.rfind('.')
    # Get the extension including the dot
    extension = lora[last_dot_position:] if last_dot_position != -1 else ""
    # Check if the extension is supported, if not, add .safetensors
    if extension not in folder_paths.supported_pt_extensions:
        lora += ".safetensors"

    # Find the matching lora path
    matching_lora = next((x for x in __list_loras() if x.endswith(lora)), None)
    if matching_lora is None:
        print(f'ComfyUI-Image-Saver: could not find full path to lora "{lora}"')
        return None
    return folder_paths.get_full_path("loras", matching_lora)

def __list_loras():
    return folder_paths.get_filename_list("loras")

def __list_embeddings():
    return folder_paths.get_filename_list("embeddings")