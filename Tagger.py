import numpy as np
import onnxruntime as ort
from PIL import Image
import json
import time
import folder_paths as comfy_paths
import os.path
import gc
import cv2

cat = "Mira/Tagger"

def decode_image(src_image):
    i = 255. * src_image[0].cpu().numpy()
    img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))    
    return img

class cl_tagger:
    '''
    CL Tagger by cella110n https://huggingface.co/cella110n
    Few codes reference from https://huggingface.co/spaces/DraconicDragon/cl_tagger
    
    Inputs:
    image           - Image for tagger
    model_name      - Onnx model
    general         - General threshold
    character       - Character threshold
    replace_space   - Replace '_' with ' ' (space)
    exclude_tags    - Exclude tags
        
    Outputs:
    tags            - Generated tags
    '''
    
    _mean = np.array([0.5, 0.5, 0.5], dtype=np.float32).reshape(3, 1, 1)
    _std = np.array([0.5, 0.5, 0.5], dtype=np.float32).reshape(3, 1, 1)
    _tag_mapping_cache = {}
    _model_cache = {}     
    _gpu_session = None
    
    def get_tag_mapping(self, full_tag_map_path):
        if full_tag_map_path not in self._tag_mapping_cache:
            print("[Mira:ClTagger] Load tag mapping: " + full_tag_map_path)
            self._tag_mapping_cache[full_tag_map_path] = self.load_tag_mapping(full_tag_map_path)        
        return self._tag_mapping_cache[full_tag_map_path]

    # onnxruntime needs 2s+ to load RAM model and create GPU version, so I leave it in RAM with CPU mode
    # GPU performance: TITAN RTX        0.088 seconds
    # CPU performance: Intel i9-9980x   0.992 seconds
    def get_session(self, model_path):
        if model_path not in self._model_cache:                
            self._model_cache[model_path] = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
        return self._model_cache[model_path]
            
    def pad_square_np(self, img_array: np.ndarray) -> np.ndarray:
        h, w, _ = img_array.shape
        if h == w:
            return img_array
        new_size = max(h, w)
        pad_top = (new_size - h) // 2
        pad_bottom = new_size - h - pad_top
        pad_left = (new_size - w) // 2
        pad_right = new_size - w - pad_left
        return np.pad(img_array, ((pad_top, pad_bottom), (pad_left, pad_right), (0, 0)),
                    mode='constant', constant_values=255)

    def preprocess_image(self, image, target_size=(448, 448)):
        img = np.array(decode_image(image))
        img = self.pad_square_np(img)
        img = cv2.resize(img, target_size, interpolation=cv2.INTER_CUBIC)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        img = img.astype(np.float32) / 255.0
        img = (img - 0.5) / 0.5
        img = np.expand_dims(np.transpose(img, (2, 0, 1)), axis=0)
        return img

    def load_tag_mapping(self, mapping_path):
        # Use the implementation from the original app.py as it was confirmed working
        with open(mapping_path, 'r', encoding='utf-8') as f: tag_mapping_data = json.load(f)
        # Check format compatibility (can be dict of dicts or dict with idx_to_tag/tag_to_category)
        if isinstance(tag_mapping_data, dict) and "idx_to_tag" in tag_mapping_data:
            idx_to_tag = {int(k): v for k, v in tag_mapping_data["idx_to_tag"].items()}
            tag_to_category = tag_mapping_data["tag_to_category"]
        elif isinstance(tag_mapping_data, dict):
            # Assuming the dict-of-dicts format from previous tests
            try:
                tag_mapping_data_int_keys = {int(k): v for k, v in tag_mapping_data.items()}
                idx_to_tag = {idx: data['tag'] for idx, data in tag_mapping_data_int_keys.items()}
                tag_to_category = {data['tag']: data['category'] for data in tag_mapping_data_int_keys.values()}
            except (KeyError, ValueError) as e:
                raise ValueError(f"Unsupported tag mapping format (dict): {e}. Expected int keys with 'tag' and 'category'.")
        else:
            raise ValueError("Unsupported tag mapping format: Expected a dictionary.")

        names = [None] * (max(idx_to_tag.keys()) + 1)
        rating, general, artist, character, copy_right, meta, quality, model_name = [], [], [], [], [], [], [], []
        for idx, tag in idx_to_tag.items():
            if idx >= len(names): names.extend([None] * (idx - len(names) + 1))
            names[idx] = tag
            category = tag_to_category.get(tag, 'Unknown') # Handle missing category mapping gracefully
            idx_int = int(idx)
            if category == 'Rating': rating.append(idx_int)
            elif category == 'General': general.append(idx_int)
            elif category == 'Artist': artist.append(idx_int)
            elif category == 'Character': character.append(idx_int)
            elif category == 'Copyright': copy_right.append(idx_int)
            elif category == 'Meta': meta.append(idx_int)
            elif category == 'Quality': quality.append(idx_int)
            elif category == 'Model': model_name.append(idx_int)

        label_data = {
            "names": names,
            "rating": rating,
            "general": general,
            "character": character,
            "copyright": copy_right,
            "artist": artist,
            "meta": meta,
            "quality": quality,
            "model": model_name
        }    
        return label_data
    
    def get_tags(self, probs, labels, gen_threshold, char_threshold):
        result = {
            "rating": [],
            "general": [],
            "character": [],
            "copyright": [],
            "artist": [],
            "meta": [],
            "quality": [],
            "model": []
        }

        # --- Rating (select max) ---
        if len(labels["rating"]) > 0:
            valid_indices = np.array([i for i in labels["rating"] if i < len(probs)])
            if len(valid_indices) > 0:
                rating_probs = probs[valid_indices]
                if len(rating_probs) > 0:
                    rating_idx_local = np.argmax(rating_probs)
                    rating_idx_global = valid_indices[rating_idx_local]
                    if rating_idx_global < len(labels["names"]) and labels["names"][rating_idx_global] is not None:
                        rating_name = labels["names"][rating_idx_global]
                        rating_conf = float(rating_probs[rating_idx_local])
                        result["rating"].append((rating_name, rating_conf))
                    else:
                        print(f"[Mira:ClTagger]Warning: Invalid global index {rating_idx_global} for rating tag.")
                else:
                    print("[Mira:ClTagger]Warning: rating_probs became empty after filtering.")
            else:
                print("[Mira:ClTagger]Warning: No valid indices found for rating tags within probs length.")

        # --- Quality (select max) ---
        if len(labels["quality"]) > 0:
            valid_indices = np.array([i for i in labels["quality"] if i < len(probs)])
            if len(valid_indices) > 0:
                quality_probs = probs[valid_indices]
                if len(quality_probs) > 0:
                    quality_idx_local = np.argmax(quality_probs)
                    quality_idx_global = valid_indices[quality_idx_local]
                    if quality_idx_global < len(labels["names"]) and labels["names"][quality_idx_global] is not None:
                        quality_name = labels["names"][quality_idx_global]
                        quality_conf = float(quality_probs[quality_idx_local])
                        result["quality"].append((quality_name, quality_conf))
                    else:
                        print(f"[Mira:ClTagger]Warning: Invalid global index {quality_idx_global} for quality tag.")
                else:
                    print("[Mira:ClTagger]Warning: quality_probs became empty after filtering.")
            else:
                print("[Mira:ClTagger]Warning: No valid indices found for quality tags within probs length.")

        # --- Threshold-based categories ---
        category_map = {
            "general": (labels["general"], gen_threshold),
            "character": (labels["character"], char_threshold),
            "copyright": (labels["copyright"], char_threshold),
            "artist": (labels["artist"], char_threshold),
            "meta": (labels["meta"], gen_threshold),
            "model": (labels["model"], gen_threshold)
        }

        for category, (indices, threshold) in category_map.items():
            if len(indices) > 0:
                valid_indices = np.array([i for i in indices if i < len(probs)])
                if len(valid_indices) > 0:
                    category_probs = probs[valid_indices]
                    mask = category_probs >= threshold
                    selected_indices_local = np.nonzero(mask)[0]
                    if len(selected_indices_local) > 0:
                        selected_indices_global = valid_indices[selected_indices_local]
                        selected_probs = category_probs[selected_indices_local]
                        for idx_global, prob_val in zip(selected_indices_global, selected_probs):
                            if idx_global < len(labels["names"]) and labels["names"][idx_global] is not None:
                                result[category].append((labels["names"][idx_global], float(prob_val)))
                            else:
                                print(f"[Mira:ClTagger]Warning: Invalid global index {idx_global} for {category} tag.")

        # --- Sort results by probability ---
        for k in result:
            result[k] = sorted(result[k], key=lambda x: x[1], reverse=True)

        return result            
    
    def run_cl_tagger(self, image, full_model_path, full_tag_map_path, general, character, replace_space, exclude):
        input_tensor = self.preprocess_image(image)
        g_labels_data = self.get_tag_mapping(full_tag_map_path)        
        session = self.get_session(full_model_path)
        
        input_name = session.get_inputs()[0].name
        output_name = session.get_outputs()[0].name
        #start_time = time.time()
        outputs = session.run([output_name], {input_name: input_tensor})[0]
        #inference_time = time.time() - start_time
        #print(f"[Mira:ClTagger]Inference completed in {inference_time:.3f} seconds")
        
        # Check for NaN/Inf in outputs
        if np.isnan(outputs).any() or np.isinf(outputs).any():
            print("[Mira:ClTagger]Warning: NaN or Inf detected in model output. Clamping...")
            outputs = np.nan_to_num(outputs, nan=0.0, posinf=1.0, neginf=0.0) # Clamp to 0-1 range

        probs = 1 / (1 + np.exp(-np.clip(outputs[0], -30, 30)))
                
        # Use the correct global variable for labels
        predictions = self.get_tags(probs, g_labels_data, general, character)

        # Format output text string
        output_tags = []
        if predictions.get("rating"): output_tags.append(predictions["rating"][0][0].replace("_", " "))
        if predictions.get("quality"): output_tags.append(predictions["quality"][0][0].replace("_", " "))
        # Add other categories, respecting order and filtering meta if needed
        for category in ["artist", "character", "copyright", "general", "meta", "model"]:
            tags_in_category = predictions.get(category, [])
            for tag, prob in tags_in_category:
                # Basic meta tag filtering for text output
                if category == "meta" and any(p in tag.lower() for p in ['id', 'commentary', 'request', 'mismatch']):
                    continue
                if replace_space:
                    output_tags.append(tag.replace("_", " "))
                else:
                    output_tags.append(tag)
        
        exclude_list = [e.strip().lower() for e in exclude.split(',') if e.strip()]
        if exclude_list:
            filtered_tags = []
            for tag in output_tags:
                tag_l = tag.lower()
                hit = False
                for ex in exclude_list:
                    if ex in tag_l:
                        hit = True
                        break
                if not hit:
                    filtered_tags.append(tag)
            output_tags = filtered_tags
        
        output_text = ", ".join(output_tags)
        print("[Mira:ClTagger] " + output_text)
        
        return output_text
    
    @classmethod
    def INPUT_TYPES(s):
        onnx_list = comfy_paths.get_filename_list("onnx")
        if 0 == len(onnx_list):
            onnx_list.insert(0, "None")
            
        return {
            "required": {
                "image":("IMAGE", {
                    "display": "input", 
                    "default": None,
                }),
                "model_name": (onnx_list, ),
                "general": ("FLOAT", {
                    "default": 0.55, 
                    "min": 0.05, 
                    "max": 1.0,
                    "step": 0.01
                }),
                "character": ("FLOAT", {
                    "default": 0.60, 
                    "min": 0.05, 
                    "max": 1.0,
                    "step": 0.01
                }),
                "replace_space": ("BOOLEAN", {
                    "default": True
                }),
                "exclude_tags":  ("STRING", {
                    "display": "input", 
                    "multiline": False
                }),
            },
        }
                
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("tags",)
    FUNCTION = "cl_tagger_ex"
    CATEGORY = cat
    
    def cl_tagger_ex(self, image, model_name, general, character, replace_space, exclude_tags):
        if model_name == 'None':
            return ("[Mira] Download CL Tagger Model and JSON file put in your \"ComfyUI/model/onnx\" foler.\nhttps://github.com/mirabarukaso/ComfyUI_Mira#tagger\nhttps://huggingface.co/cella110n", )
        
        full_model_path = comfy_paths.get_full_path('onnx', model_name)
        full_tag_map_path = full_model_path.replace('.onnx', '_tag_mapping.json')
        if not os.path.exists(full_model_path):
            print(f"[Mira:ClTagger]Error: [{full_model_path}] not found!")
            return (f"[Mira:ClTagger]Error: [{full_model_path}] not found!",)
        
        if not os.path.exists(full_tag_map_path):
            print(f"[Mira:ClTagger]Error: [{full_model_path}] not found!")
            return (f"[Mira:ClTagger]Error: [{full_model_path}] not found!", )
        
        result = self.run_cl_tagger(image, full_model_path, full_tag_map_path, general, character, replace_space, exclude_tags)
        
        return (result,)