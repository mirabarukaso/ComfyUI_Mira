import logging
logger = logging.getLogger("comfy")
import os
from pathlib import Path
import hashlib
from tqdm import tqdm
import folder_paths

# Full-file SHA256. The first 10 hex chars are Civitai AutoV2.
# Sidecar format: "<64 hex>\n<mtime_ns> <size>\n". A legacy file is a single hash line.


def _is_sha256_hex(value: str) -> bool:
    if len(value) != 64:
        return False
    try:
        int(value, 16)
    except ValueError:
        return False
    return True


def _cache_stamp(file_stat: os.stat_result) -> str:
    return f"{file_stat.st_mtime_ns} {file_stat.st_size}"


def _read_cached_sha256(hash_file: str, file_stat: os.stat_result) -> str | None:
    if not os.path.isfile(hash_file):
        return None
    try:
        with open(hash_file, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
    except OSError as e:
        logger.error(f"ComfyUI-Image-Saver: Error reading existing hash file: {e}")
        return None

    if not lines or not _is_sha256_hex(lines[0]):
        return None

    digest = lines[0].lower()
    stamp = _cache_stamp(file_stat)
    if len(lines) >= 2:
        if lines[1] == stamp:
            return digest
        logger.info(f"ComfyUI-Image-Saver: Hash cache is stale for '{Path(hash_file).stem}', recalculating")
        return None

    # Legacy sidecar with no stamp. Keep it only when the model was not modified after the hash was written.
    try:
        hash_mtime_ns = os.stat(hash_file).st_mtime_ns
    except OSError as e:
        logger.error(f"ComfyUI-Image-Saver: Error reading existing hash file: {e}")
        return None
    if file_stat.st_mtime_ns <= hash_mtime_ns:
        _write_cached_sha256(hash_file, digest, file_stat)
        return digest

    logger.info(f"ComfyUI-Image-Saver: Hash cache is stale for '{Path(hash_file).stem}', recalculating")
    return None


def _write_cached_sha256(hash_file: str, digest: str, file_stat: os.stat_result) -> None:
    temporary = hash_file + ".tmp"
    try:
        with open(temporary, "w", encoding="utf-8", newline="\n") as f:
            f.write(f"{digest}\n{_cache_stamp(file_stat)}\n")
        os.replace(temporary, hash_file)
    except OSError as e:
        logger.error(f"ComfyUI-Image-Saver: Error writing hash to {hash_file}: {e}")
        try:
            os.remove(temporary)
        except OSError:
            pass


def _compute_sha256(file_path: str, file_size: int) -> str:
    sha256_hash = hashlib.sha256()
    block_size = 1048576  # 1 MB
    logger.info(f"ComfyUI-Image-Saver: Calculating sha256 for '{Path(file_path).stem}'")
    with open(file_path, "rb") as f:
        with tqdm(None, None, file_size, unit="B", unit_scale=True, unit_divisor=1024) as progress_bar:
            for byte_block in iter(lambda: f.read(block_size), b""):
                progress_bar.update(len(byte_block))
                sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def get_sha256(file_path: str):
    file_stat = os.stat(file_path)
    hash_file = os.path.splitext(file_path)[0] + ".sha256"
    cached = _read_cached_sha256(hash_file, file_stat)
    if cached is not None:
        return cached

    digest = _compute_sha256(file_path, file_stat.st_size)
    _write_cached_sha256(hash_file, digest, file_stat)
    return digest


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


def normalize_model_name(name: str) -> str:
    """Turn Windows separators and doubled backslashes into a ComfyUI relative name."""
    name = name.strip().strip('"').strip("'")
    name = name.replace("\\", "/")
    while "//" in name:
        name = name.replace("//", "/")
    if name.startswith("./"):
        name = name[2:]
    return name.lstrip("/")


def _candidate_names(name: str) -> list[str]:
    normalized = normalize_model_name(name)
    if not normalized or normalized.endswith("/"):
        return []
    extension = os.path.splitext(normalized)[1].lower()
    if extension in folder_paths.supported_pt_extensions:
        return [normalized]
    extensions = [".safetensors"]
    for ext in sorted(folder_paths.supported_pt_extensions):
        if ext not in extensions:
            extensions.append(ext)
    return [normalized + ext for ext in extensions]


def _full_model_path_for(folder_name: str, name: str, label: str):
    candidates = _candidate_names(name)
    if not candidates:
        logger.warning(f'ComfyUI-Image-Saver: could not find full path to {label} "{name}"')
        return None

    for candidate in candidates:
        found = folder_paths.get_full_path(folder_name, candidate)
        if found:
            return found

    listed = [(item, normalize_model_name(item)) for item in folder_paths.get_filename_list(folder_name)]
    matches = []
    for candidate in candidates:
        hits = [item for item, normalized in listed if normalized == candidate or normalized.endswith("/" + candidate)]
        if hits:
            matches = list(dict.fromkeys(hits))
            break

    if len(matches) == 1:
        return folder_paths.get_full_path(folder_name, matches[0])
    if len(matches) > 1:
        shown = ", ".join(normalize_model_name(item) for item in matches)
        logger.warning(f'ComfyUI-Image-Saver: multiple files match {label} "{name}": {shown}')
        return None

    logger.warning(f'ComfyUI-Image-Saver: could not find full path to {label} "{name}"')
    return None


def full_embedding_path_for(embedding: str):
    return _full_model_path_for("embeddings", embedding, "embedding")


def full_lora_path_for(lora: str):
    return _full_model_path_for("loras", lora, "lora")
