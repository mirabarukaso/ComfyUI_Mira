import re
from typing import List
from comfy.sd1_clip import escape_important, unescape_important, token_weights

from .utils import civitai_embedding_key_name, civitai_lora_key_name, full_embedding_path_for, full_lora_path_for, get_sha256

"""
Extracts Embeddings and Lora's from the given prompts
and allows asking for their sha's
This module is based on civit's plugin and website implementations
The image saver node goes through the automatic flow, not comfy, on civit
see: https://github.com/civitai/sd_civitai_extension/blob/2008ba9126ddbb448f23267029b07e4610dffc15/scripts/gen_hashing.py
see: https://github.com/civitai/civitai/blob/d83262f401fb372c375e6222d8c2413fa221c2c5/src/utils/metadata/automatic.metadata
"""
class PromptMetadataExtractor:
    # Anything that follows embedding:<characters except , or whitespace
    EMBEDDING = r'embedding:([^,\s\(\)\:]+)'
    # Anything that follows <lora:NAME> with allowance for :weight, :weight.fractal or LBW
    LORA = r'<lora:([^>:]+)(?::([^>]+))?>'

    def __init__(self, prompts: List[str]):
        self.__embeddings = {}
        self.__loras = {}
        self.__perform(prompts)

    """
    Returns the embeddings used in the given prompts in a format as known by civitAI
    Example output: {"embed:EasyNegative": "66a7279a88", "embed:FastNegativeEmbedding": "687b669d82", "embed:ng_deepnegative_v1_75t": "54e7e4826d", "embed:imageSharpener": "fe5a4dfc4a"}
    """
    def get_embeddings(self):
        return self.__embeddings

    """
    Returns the lora's used in the given prompts in a format as known by civitAI
    Example output: {"LORA:epi_noiseoffset2": "81680c064e", "LORA:GoodHands-beta2": "ba43b0efee"}
    """
    def get_loras(self):
        return self.__loras

    # Private API
    def __perform(self, prompts):
        for prompt in prompts:
            # Use ComfyUI's built-in attention parser to get accurate weights for embeddings
            parsed = ((unescape_important(value), weight) for value, weight in token_weights(escape_important(prompt), 1.0))
            for text, weight in parsed:
                embeddings = re.findall(self.EMBEDDING, text, re.IGNORECASE | re.MULTILINE)
                for embedding in embeddings:
                    self.__extract_embedding_information(embedding, weight)

            loras = re.findall(self.LORA, prompt, re.IGNORECASE | re.MULTILINE)
            for lora in loras:
                self.__extract_lora_information(lora)

    def __extract_embedding_information(self, embedding: str, weight: float):
        embedding_name = civitai_embedding_key_name(embedding)
        embedding_path = full_embedding_path_for(embedding)
        if embedding_path == None:
            return
        sha = self.__get_shortened_sha(embedding_path)
        # Based on https://github.com/civitai/sd_civitai_extension/blob/2008ba9126ddbb448f23267029b07e4610dffc15/scripts/gen_hashing.py#L53
        self.__embeddings[embedding_name] = (embedding_path, weight, sha)

    def __extract_lora_information(self, lora: tuple[str, str]):
        lora_name = civitai_lora_key_name(lora[0])
        lora_path = full_lora_path_for(lora[0])
        if lora_path == None:
            return
        try:
            lora_weight = float(lora[1].split(':')[0])
        except (ValueError, TypeError):
            lora_weight = 1
        sha = self.__get_shortened_sha(lora_path)
        # Based on https://github.com/civitai/sd_civitai_extension/blob/2008ba9126ddbb448f23267029b07e4610dffc15/scripts/gen_hashing.py#L63
        self.__loras[lora_name] = (lora_path, lora_weight, sha)

    def __get_shortened_sha(self, file_path: str):
       return get_sha256(file_path)[:10]