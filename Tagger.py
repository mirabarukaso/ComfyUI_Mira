import numpy as np
import onnxruntime as ort
import torchvision.transforms as transforms
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
    categories      - Selected categories in generate tags, and order by input order
    exclude_tags    - Exclude tags
    session_method  - Tagger Model in CPU or GPU session. Release will release session after generate
        
    Outputs:
    tags            - Generated tags
    '''
    
    _mean = np.array([0.5, 0.5, 0.5], dtype=np.float32).reshape(3, 1, 1)
    _std = np.array([0.5, 0.5, 0.5], dtype=np.float32).reshape(3, 1, 1)
    _tag_mapping_cache = {}
    _cpu_session = None
    _gpu_session = None
    
    def get_tag_mapping(self, full_tag_map_path):
        if full_tag_map_path not in self._tag_mapping_cache:
            print("[Mira:ClTagger] Load tag mapping: " + full_tag_map_path)
            self._tag_mapping_cache[full_tag_map_path] = self.load_tag_mapping(full_tag_map_path)        
        return self._tag_mapping_cache[full_tag_map_path]

    # onnxruntime needs 2s+ to load RAM model and create GPU version, so I leave it in RAM with CPU mode
    # GPU performance: TITAN RTX        0.088 seconds       "CUDAExecutionProvider", "CPUExecutionProvider"
    # CPU performance: Intel i9-9980x   0.992 seconds       "CPUExecutionProvider"
    def get_session(self, model_path, session_method):
        if session_method.startswith('CPU'):
            if not self._cpu_session:                
                self._cpu_session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
            return self._cpu_session
        elif session_method.startswith('GPU'):
            if not self._gpu_session:
                self._gpu_session = ort.InferenceSession(model_path, providers=["CUDAExecutionProvider", "CPUExecutionProvider"])
            return self._gpu_session
        
            
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
    
    def run_cl_tagger(self, image, full_model_path, full_tag_map_path, general, character, replace_space, categories, exclude, session_method):
        input_tensor = self.preprocess_image(image)
        g_labels_data = self.get_tag_mapping(full_tag_map_path)
        session = self.get_session(full_model_path, session_method)
        
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

        # Get required categories
        categories_select = [c.strip() for c in categories.split(',') if c.strip()]
        
        # Format output text string respecting category order
        output_tags = []

        for category in categories_select:
            if category not in predictions:
                continue
            tags_in_category = predictions.get(category, [])

            # only use the most scored tag
            if category in ["rating", "quality"]:
                if tags_in_category:
                    tag_name = tags_in_category[0][0]
                    if replace_space:
                        tag_name = tag_name.replace("_", " ")
                    output_tags.append(tag_name)
                continue
                
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
        
        if session_method.endswith('Release'):
            session = None
            self._cpu_session = None
            self._gpu_session = None
            gc.collect()
            
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
                "categories" : ("STRING", {
                    "default": 'rating,artist,general,character,copyright,meta,model,quality', 
                    "display": "input", 
                    "multiline": False
                }),
                "exclude_tags":  ("STRING", {
                    "display": "input", 
                    "multiline": False
                }),
                "session_method" : (['CPU', 'CPU Release', 'GPU', 'GPU Release'], ),
            },
        }
                
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("tags",)
    FUNCTION = "cl_tagger_ex"
    CATEGORY = cat
    
    def cl_tagger_ex(self, image, model_name, general, character, replace_space, categories, exclude_tags, session_method):
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
        
        result = self.run_cl_tagger(image, full_model_path, full_tag_map_path, general, character, replace_space, categories, exclude_tags, session_method)
        
        return (result,)
    
class camie_tagger:
    '''
    Camie Tagger by Camais03 https://huggingface.co/Camais03
    Few codes reference from https://huggingface.co/spaces/Camais03/camie-tagger-v2-app/tree/main/utils
    
    Inputs:
    image           - Image for tagger
    model_name      - Onnx model
    general         - General threshold
    min_confidence  - Minimum confidence to display
    replace_space   - Replace '_' with ' ' (space)
    categories      - Selected categories in generate tags, and order by input order
    exclude_tags    - Exclude tags
    session_method  - Tagger Model in CPU or GPU session. Release will release session after generate
        
    Outputs:
    tags            - Generated tags
    '''
    
    _tag_mapping_cache = {}
    _cpu_session = None
    _gpu_session = None
    
    def get_tag_mapping(self, full_tag_map_path):
        if full_tag_map_path not in self._tag_mapping_cache:
            print("[Mira:CamieTagger] Load tag mapping: " + full_tag_map_path)
            with open(full_tag_map_path, "r") as f: metadata = json.load(f)
            
            try:
                tag_mapping = metadata["dataset_info"]["tag_mapping"]
                if not tag_mapping["idx_to_tag"] :
                    raise ValueError("[Mira:CamieTagger]Error: Invalid tag mapping structure in metadata");
            except Exception as e:
                raise ValueError(f"[Mira:CamieTagger]Error:{e}")
            
            self._tag_mapping_cache[full_tag_map_path] = tag_mapping
        return self._tag_mapping_cache[full_tag_map_path]
        
    def get_session(self, model_path, session_method):
        if session_method.startswith('CPU'):
            if not self._cpu_session:                
                self._cpu_session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
            return self._cpu_session
        elif session_method.startswith('GPU'):
            if not self._gpu_session:
                self._gpu_session = ort.InferenceSession(model_path, providers=["CUDAExecutionProvider", "CPUExecutionProvider"])
            return self._gpu_session
        
    def preprocess_image(self, image, image_size=512):
        """
        Process an image for ImageTagger inference with proper ImageNet normalization
        """                
        # ImageNet normalization - CRITICAL for your model
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406], 
                std=[0.229, 0.224, 0.225]
            )
        ])
        
        with decode_image(image) as img:
            # Convert RGBA or Palette images to RGB
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Get original dimensions
            width, height = img.size
            aspect_ratio = width / height
            
            # Calculate new dimensions to maintain aspect ratio
            if aspect_ratio > 1:
                new_width = image_size
                new_height = int(new_width / aspect_ratio)
            else:
                new_height = image_size
                new_width = int(new_height * aspect_ratio)
            
            # Resize with LANCZOS filter
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Create new image with padding (use ImageNet mean for padding)
            # Using RGB values close to ImageNet mean: (0.485*255, 0.456*255, 0.406*255)
            pad_color = (124, 116, 104)
            new_image = Image.new('RGB', (image_size, image_size), pad_color)
            paste_x = (image_size - new_width) // 2
            paste_y = (image_size - new_height) // 2
            new_image.paste(img, (paste_x, paste_y))
            
            # Apply transforms (including ImageNet normalization)
            img_tensor = transform(new_image)
            img_array = img_tensor.numpy()
            img_array = np.expand_dims(img_array, axis=0)  # Convert CHW → BCHW
            return img_array
    
    def run_camie_tagger(self, image, full_model_path, full_tag_map_path, general, min_confidence, replace_space, categories, exclude, session_method):
        input_tensor = self.preprocess_image(image)        
        g_labels_data = self.get_tag_mapping(full_tag_map_path)            
        session = self.get_session(full_model_path, session_method)
                
        input_name = session.get_inputs()[0].name
        output_name = session.get_outputs()[0].name
        #start_time = time.time()
        outputs = session.run([output_name], {input_name: input_tensor})[0]
        #inference_time = time.time() - start_time
        #print(f"[Mira:CamieTagger]Inference completed in {inference_time:.3f} seconds")
        
        # Process outputs - handle both single and multi-output models
        if len(outputs) >= 2:
            # Multi-output model (initial_predictions, refined_predictions, selected_candidates)
            #initial_logits = outputs[0]
            refined_logits = outputs[1]
            # Use refined predictions as main output
            main_logits = refined_logits
        else:
            # Single output model
            main_logits = outputs[0]
            
        # Apply sigmoid to get probabilities
        main_probs = 1.0 / (1.0 + np.exp(-main_logits))

        # Ensure the output always has a batch dimension
        if main_probs.ndim == 1:
            main_probs = np.expand_dims(main_probs, axis=0)

        for i in range(main_probs.shape[0]):
            probs = main_probs[i]            
            
            # Extract and organize all probabilities
            all_probs = {}
            for idx in range(probs.shape[0]):
                prob_value = float(probs[idx])
                if prob_value >= min_confidence:
                    idx_str = str(idx)
                    tag_name = g_labels_data["idx_to_tag"].get(idx_str, f"unknown-{idx}")
                    category = g_labels_data["tag_to_category"].get(tag_name, "general")
                    
                    if category not in all_probs:
                        all_probs[category] = []
                    
                    all_probs[category].append((tag_name, prob_value))
            
            # Sort tags by probability within each category
            for category in all_probs:
                all_probs[category] = sorted(
                    all_probs[category], 
                    key=lambda x: x[1], 
                    reverse=True
                )
            
            # Get the filtered tags based on the selected threshold
            tags = {}
            category_thresholds = {}
            for category, cat_tags in all_probs.items():
                # Use category-specific threshold if available
                if category_thresholds and category in category_thresholds:
                    cat_threshold = category_thresholds[category]
                else:
                    cat_threshold = general
                    
                tags[category] = [(tag, prob) for tag, prob in cat_tags if prob >= cat_threshold]
            
            # Filter and sort tags by input categories
            categories_select = [c.strip() for c in categories.split(',') if c.strip()]

            # Create filtered tags based on input categories, preserving order
            all_tags = []
            for category in categories_select:
                if category not in tags:
                    continue
                cat_tags = tags[category]
                for tag, _ in cat_tags:
                    if replace_space:
                        all_tags.append(tag.replace('_', ' '))
                    else:
                        all_tags.append(tag)
        
        output_tags = all_tags
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
        print("[Mira:CamieTagger] " + output_text)
        
        if session_method.endswith('Release'):
            session = None
            self._cpu_session = None
            self._gpu_session = None
            gc.collect()
            
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
                    "default": 0.49, 
                    "min": 0.05, 
                    "max": 1.0,
                    "step": 0.01
                }),
                "min_confidence": ("FLOAT", {
                    "default": 0.01, 
                    "min": 0.01, 
                    "max": 0.5,
                    "step": 0.01
                }),
                "replace_space": ("BOOLEAN", {
                    "default": True
                }),
                "categories" : ("STRING", {
                    "default": 'rating,artist,general,character,copyright,meta,year', 
                    "display": "input", 
                    "multiline": False
                }),
                "exclude_tags":  ("STRING", {
                    "display": "input", 
                    "multiline": False
                }),
                "session_method" : (['CPU', 'CPU Release', 'GPU', 'GPU Release'], ),
            },
        }
                
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("tags",)
    FUNCTION = "camie_tagger_ex"
    CATEGORY = cat
    
    def camie_tagger_ex(self, image, model_name, general, min_confidence, replace_space, categories, exclude_tags, session_method):
        if model_name == 'None':
            return ("[Mira] Download Camie Tagger Model and JSON file put in your \"ComfyUI/model/onnx\" foler.\nhttps://github.com/mirabarukaso/ComfyUI_Mira#tagger\nhttps://huggingface.co/Camais03", )
        
        full_model_path = comfy_paths.get_full_path('onnx', model_name)
        full_tag_map_path = full_model_path.replace('.onnx', '-metadata.json')
        if not os.path.exists(full_model_path):
            print(f"[Mira:CamieTagger]Error: [{full_model_path}] not found!")
            return (f"[Mira:CamieTagger]Error: [{full_model_path}] not found!",)
        
        if not os.path.exists(full_tag_map_path):
            print(f"[Mira:CamieTagger]Error: [{full_model_path}] not found!")
            return (f"[Mira:CamieTagger]Error: [{full_model_path}] not found!", )
        
        result = self.run_camie_tagger(image, full_model_path, full_tag_map_path, general, min_confidence, replace_space, categories, exclude_tags, session_method)
        
        return (result,)
