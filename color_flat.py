import cv2
import torch
import numpy as np
import torch
import torch.nn.functional as F

def kmeans_gpu_soft(x, n_clusters=20, n_iter=10, temperature=1.0):
    """
    temperature: more soft when larger, more hard when smaller
    """
    N, _ = x.shape
    device = x.device

    # initialize centers randomly
    indices = torch.randperm(N, device=device)[:n_clusters]
    centers = x[indices]

    for _ in range(n_iter):
        # calculate distances and get soft assignments via softmax
        dist = torch.cdist(x, centers)  # [N, K]
        weights = F.softmax(-dist / temperature, dim=1)  # [N, K]
        
        # assign new centers based on soft assignments
        new_centers = torch.mm(weights.T, x) / (weights.sum(dim=0, keepdim=True).T + 1e-8)
        centers = new_centers
    
    return weights, centers

def bilateral_smooth(img, d=9, sigma_color=75, sigma_space=75):
    # blateral filter smoothing
    img_np = img.cpu().numpy().astype(np.uint8)
    smoothed = cv2.bilateralFilter(img_np, d, sigma_color, sigma_space)
    
    del img_np
    torch.cuda.empty_cache()
    return torch.from_numpy(smoothed).float().to(img.device)

def sharpen(img, sigma=1.0, strength=1.0):
    # Unsharp mask sharpening using Gaussian blur
    # Ensure image is in [C, H, W] format for convolution
    img = img.permute(2, 0, 1).unsqueeze(0)  # [1, C, H, W]
    
    # Create Gaussian kernel
    kernel_size = int(6 * sigma + 1)  # Ensure odd kernel size
    if kernel_size % 2 == 0:
        kernel_size += 1
    gaussian_kernel = torch.exp(-torch.arange(-(kernel_size//2), kernel_size//2 + 1, device=img.device)**2 / (2 * sigma**2))
    gaussian_kernel = gaussian_kernel / gaussian_kernel.sum()
    
    # Reshape for horizontal and vertical kernels
    kernel_h = gaussian_kernel.view(1, 1, 1, kernel_size).repeat(3, 1, 1, 1)  # [3, 1, 1, kernel_size]
    kernel_v = gaussian_kernel.view(1, 1, kernel_size, 1).repeat(3, 1, 1, 1)  # [3, 1, kernel_size, 1]
    
    # Apply separable Gaussian blur
    blurred = F.conv2d(img, kernel_h, groups=3, padding=(0, kernel_size//2))
    blurred = F.conv2d(blurred, kernel_v, groups=3, padding=(kernel_size//2, 0))
    
    # Compute unsharp mask
    sharpened = img + strength * (img - blurred)
    
    # Return to [H, W, C] format
    sharpened = sharpened.squeeze(0).permute(1, 2, 0)
    
    del img, blurred, kernel_h, kernel_v, gaussian_kernel
    torch.cuda.empty_cache()
    return sharpened.clamp(0, 255)

def process_block(img_block, n_colors, spatial_scale, scale, temperature, device="cuda"):
    # Process a single image block with clustering and reconstruction
    h, w, _ = img_block.shape
    img_tensor = torch.from_numpy(img_block).float().to(device)
    img_flat = img_tensor.reshape(-1, 3)
    
    # Spatial features
    xx, yy = torch.meshgrid(torch.arange(h, device=device),
                            torch.arange(w, device=device),
                            indexing="ij")
    
    features = torch.cat([
        img_flat,
        xx.reshape(-1, 1).float() / h * spatial_scale * scale,
        yy.reshape(-1, 1).float() / w * spatial_scale * scale
    ], dim=1)
    
    # Clustering
    weights, centers = kmeans_gpu_soft(features, n_clusters=n_colors, temperature=temperature)
    
    # Reconstruction
    rgb_centers = centers[:, :3]
    dist_to_pixels = torch.cdist(rgb_centers, img_flat)
    closest_pixel_indices = dist_to_pixels.argmin(dim=1)
    new_colors = img_flat[closest_pixel_indices]
    
    out_flat = torch.mm(weights, new_colors)
    out = out_flat.reshape(h, w, 3)
    return out

def flat_color_multi_scale(image_input, n_colors=20, scales=[1.0, 0.5, 0.25], 
                          spatial_scale=50, temperature=2.0, sharpen_strength=1.0,
                          block_size=512):
    """
    Multi-scale flat color processing to reduce layering, with sharpening post-processing, 
    supports block processing to reduce VRAM usage
    """
    with torch.no_grad():
        img_rgb = image_input
        if img_rgb.shape[2] != 3:
            raise ValueError("Input image must have 3 channels (RGB).")
        
        # Apply bilateral filter
        denoised = cv2.bilateralFilter(img_rgb, d=9, sigmaColor=75, sigmaSpace=75)
        
        # Texture enhancement: Unsharp Masking
        blurred = cv2.GaussianBlur(denoised, (5, 5), sigmaX=1.0)
        sharpened = cv2.addWeighted(denoised, 1.5, blurred, -0.5, 0)
        del denoised, blurred
    
        img_rgb = sharpened
        
        h, w, _ = img_rgb.shape
        results = []
        
        for scale in scales:
            # Resize image
            new_h, new_w = int(h * scale), int(w * scale)
            img_resized = cv2.resize(img_rgb, (new_w, new_h))
            
            # Check if block processing is needed
            if new_h > block_size or new_w > block_size:
                block_results = np.zeros((new_h, new_w, 3), dtype=np.uint8)
                step_h = block_size
                step_w = block_size
                
                for i in range(0, new_h, step_h):
                    for j in range(0, new_w, step_w):
                        # Extract block, slightly expand boundaries to avoid seams
                        i_end = min(i + step_h, new_h)
                        j_end = min(j + step_w, new_w)
                        block = img_resized[i:i_end, j:j_end]
                        
                        # Process block
                        out_block = process_block(block, n_colors, spatial_scale, scale, temperature)
                        out_block_np = out_block.clamp(0, 255).byte().cpu().numpy()
                        block_results[i:i_end, j:j_end] = out_block_np
                        
                        # Clear GPU memory
                        torch.cuda.empty_cache()
                
                out_resized = cv2.resize(block_results, (w, h))
                results.append(torch.from_numpy(out_resized).float().to("cuda"))
            else:
                # Directly process the entire resized image
                out = process_block(img_resized, n_colors, spatial_scale, scale, temperature)
                out_np = out.clamp(0, 255).byte().cpu().numpy()
                out_resized = cv2.resize(out_np, (w, h))
                results.append(torch.from_numpy(out_resized).float().to("cuda"))
        
        # Combine multi-scale results
        final_result = sum(results) / len(results)
        
        # post-processing - bilateral smoothing
        final_result = bilateral_smooth(final_result, d=11, sigma_color=35, sigma_space=70)
        
        # post-processing - sharpening
        if sharpen_strength > 0.01:
            final_result = sharpen(final_result, sigma=1.0, strength=sharpen_strength)
        
        out_img = final_result.clamp(0, 255).byte().cpu().numpy()
        
        # Clean up final tensors and clear VRAM
        del final_result, results
        torch.cuda.empty_cache()
            
        return out_img
    
