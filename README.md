# ComfyUI_Mira
A custom node for [ComfyUI](https://github.com/comfyanonymous/ComfyUI/) to improve all those custom nodes I feel not comfortable in my workflow.

------

## Installation
Search `ComfyUI_Mira` in your `ComfyUI` -> `Manager` -> `Custom Nodes Manager`, then click `Install`   

or   

`Clone` the repository to custom_nodes in your `ComfyUI\custom_nodes` directory:   
```
git clone https://github.com/mirabarukaso/ComfyUI_Mira.git
```

If you got error report on loading, you may need run the following command in `ComfyUI\custom_nodes\ComfyUI_Mira` or `ComfyUI\custom_nodes\mira`:   
```
pip install -r requirements.txt
```

------

## Functions   
### Mask
Before you start, check [the simple example for Regional Condition](https://github.com/mirabarukaso/ComfyUI_Mira/issues/12#issuecomment-2727190727)

Create Tilling PNG Mask   
Create a `Tilling` PNG image with Color Mask stack for regional conditioning mask.   
Ideas from [sd-webui-regional-prompter](https://github.com/hako-mikan/sd-webui-regional-prompter)

| Inputs | Description |
| --- | --- |
| `Width`  `Height` | Image size, could be difference with cavan size, but recommended to connect them together. |
| `Colum_first` | A boolean trigger, when enabled, will treat default cut as a horizontal cut. |
| `Rows`  `Colums` |  Define how many `Blocks` you want, all `Blocks` are the same weight. (Blocks = Rows x Colums) <br />  ***Low prority, only works when Layout is incorrect.*** |
| `Layout` | Customized `Blocks` with layouts input. e.g. `1,2,1,1;2,4,6`<br /> `0-9` `,` `;` Check Examples section for more detail. <br />***High prority, in case you don't need custom layout, simply put `#` here.*** |   

| Outputs | Description |
| --- | --- |
| `Image` | Visualisation Image of your Layout. |
| `PngColorMasks` | A List contains all your Blocks' color information.  <br />Connect to `Create PNG Mask ` `Color Mask to HEX String` `Color Mask to INT RGB` `Color Masks List` |
| `PngRectangles` | A List contains all PNG Blocks' rectangle informationm, last one is the whole Image's Width and Height. |
| `Debug` | Debug information as String. |

| Examples | Description |
| --- | --- |
| `0-9` | Block weights |
| `,` | A normal segmentation. Let's call it `N` cut|
| `;` | A high-priority segmentation perpendicular to the normal direction. Let's call it `G` cut|
| `1,2,1,1;2,4,6` <br /> `Colum_first ENABLED`| When combining `,` and `;`, the first and the following `;` elements are treated as the weight of `G` for current cavans. Node will first split the canvas with weight `1` and `;2` as `G` cuts. Then split the following parts with `2,1,1` and `4,6` as `N` cuts.  <br />***NOTE: The arithmetic logic here are different from WebUI, please use "Colum_first" if you need to change the direction, don't replace `,` and `;` directly.*** |
| `1,2,3,2,1` <br /> `Colum_first DISABLED`| A simple horizontal `N` cut with weights. |
| `1,2,3,2,1` <br /> `Colum_first ENABLED`| A simple vertical `N` cut with weights. |

| ***1,2,1,1;2,4,6 with Colum_first*** | ***1,2,3,2,1*** | ***1,2,3,2,1 with Colum_first*** |
| --- | --- | --- |
| <img src="https://github.com/mirabarukaso/ComfyUI_Mira/blob/main/examples/example_mask2rgb.png" width=35% height=35%> | <img src="https://github.com/mirabarukaso/ComfyUI_Mira/blob/main/examples/example_mask2rgb_12321_f.png" width=35% height=35%> | <img src="https://github.com/mirabarukaso/ComfyUI_Mira/blob/main/examples/example_mask2rgb_12321_t.png" width=35% height=35%> |

------
Create Nested Rectangles PNG Mask   
Create a `Nested Rectangles` PNG image with Color Mask stack for regional conditioning mask.   
Ideas from [Watermark Removal](https://github.com/mirabarukaso/ComfyUI_Mira?tab=readme-ov-file#create-watermark-removal-mask)   

| Inputs | Description |
| --- | --- |
| `Width`  `Height` | Image size, could be difference with cavan size, but recommended to connect them together. |
| `X`, `Y` |  Center point (`X`,`Y`) of all Rectangles. |    
| `unlimit_top` | When `ENABLED`, all `masks` will create from the top of Image. |
| `unlimit_bottom` | When `ENABLED`, all `masks` will create till the bottom of Image. |
| `unlimit_left` | When `ENABLED`, all `masks` will create from the left of Image. |
| `unlimit_right` | When `ENABLED`, all `masks` will create till the right of Image. |        
| `Layout` | Customized `Blocks` with layouts input. e.g. `2,4,1` <br /> `0-9` `,` `;` Check Examples section for more detail. |
        
| Outputs | Description |
| --- | --- |
| `Image` | Visualisation Image of your Layout. |
| `PngColorMasks` | A List contains all your Blocks' color information.  <br />Connect to `Create PNG Mask ` `Color Mask to HEX String` `Color Mask to INT RGB` `Color Masks List` |
| `PngRectangles` | A List contains all PNG Blocks' rectangle informationm, last one is the whole Image's Width and Height. |
| `Debug` | Debug information as String. |


| Examples | Description |
| --- | --- |
| `0-9` | Block weights |
| `,` | A normal segmentation.  `;` will treat as same as `,` |
| `;` | Ignored in `,  ;` |

| ***2,4,1*** | ***2,4,1 unlimit bottom*** | ***2,4,1 unlimit bottom and right and blur 16*** |
| --- | --- | --- |
| <img src="https://github.com/mirabarukaso/ComfyUI_Mira/blob/main/examples/example_createnestedpng.png" width=35% height=35%> | <img src="https://github.com/mirabarukaso/ComfyUI_Mira/blob/main/examples/example_createnestedpng_ub.png" width=35% height=35%> | <img src="https://github.com/mirabarukaso/ComfyUI_Mira/blob/main/examples/example_createnestedpng_ubr_b16.png" width=35% height=35%> |

------
PngColor Masks to Mask List   
Convert ranged `PngColorMasks` to Masks with(or without) Blur. **Dunno if there is a proper way to solve the output problem.**   
Ideas from [ComfyUI_essentials](https://github.com/cubiq/ComfyUI_essentials)

| Inputs | Description |
| --- | --- |
| `Image` | Image from ` Mira/Mask/Create PNG Mask` |
| `PngColorMasks` | List from ` Mira/Mask/Create PNG Mask` |
| `Blur` | The intensity of blur around the edge of Mask, set to `0` for a solid edge. |
| `Start_At_Index` | The first block index number you want. |

| Outputs | Description |
| --- | --- |
| `mask_[0-9]` | The Mask for `Regional Conditioning` or ***Anything*** who need a Mask. |

| ***Solid*** | ***Blur 16.0*** |
| --- | --- |
| <img src="https://github.com/mirabarukaso/ComfyUI_Mira/blob/main/examples/example_mask2mask_solid.png" width=35% height=35%> | <img src="https://github.com/mirabarukaso/ComfyUI_Mira/blob/main/examples/example_mask2mask_blur.png" width=35% height=35%> |

------
PngColor Mask to HEX String   
Convert specified `Index` of `PngColorMasks` to HEX value. e.g. `RGB(255,0,255)` to `#FF00FF`

| Inputs | Description |
| --- | --- |
| `PngColorMasks` | List from ` Mira/Mask/Create PNG Mask` |
| `Index` | The block index number. |

| Outputs | Description |
| --- | --- |
| `mask_color` | The color RGB in HEX for `Regional Conditioning By Color Mask (Inspire)` or etc. |

------
PngColor Mask to INT RGB    
Convert specified `Index` `PngColorMasks` to RGB value for `🔧 Mask From Color` or etc. e.g. `RGB(255,0,255)` 

| Inputs | Description |
| --- | --- |
| `PngColorMasks` | List from ` Mira/Mask/Create PNG Mask` |
| `Index` | The block index number. |

| Outputs | Description |
| --- | --- |
| `R` | Red |
| `G` | Green |
| `B` | Blue |

------
PngColor Masks to List   
Convert ranged `PngColorMasks` to HEX value. **Dunno if there is a proper way to solve the output problem.**

| Inputs | Description |
| --- | --- |
| `PngColorMasks` | List from ` Mira/Mask/Create PNG Mask` |
| `Start_At_Index` | The first block index number you want. |

| Outputs | Description |
| --- | --- |
| `mask_color_[0-9]` | The color RGB in HEX for `Regional Conditioning By Color Mask (Inspire)` or etc. |

------
PngRectangles to Mask (List)    
Convert ranged `PngRectangles` to Mask with Mask `Intenisity` and `Blur` function.

| Inputs (Common) | Description |
| --- | --- |
| `PngRectangles` | List from ` Mira/Mask/Create PNG Mask` |
| `Intenisity` | `Intenisity` of Mask, set to `1.0` for solid Mask. |
| `Blur` | The intensity of blur around the edge of Mask, set to `0` for a solid edge. |
| `Start_At_Index` | The first block index number you want. |

| Inputs (Single Mask) | Description |
| --- | --- |
| `Overlap` | Combine the `Previous` or `Next` Masks into current Mask. `None` for disable. |
| `Overlap_Count` | How many `Previous` or `Next` Masks you want to combine. |

| Outputs | Description |
| --- | --- |
| Normal |
| `mask` | Mask with specified `Intenisity` and `Blur`. |
| List |
| `mask_[0-9]` | Masks List with specified `Intenisity` and `Blur`. |

Example   
| ***Normal*** | ***Overlap*** |
| --- | --- |
| <img src="https://github.com/mirabarukaso/ComfyUI_Mira/blob/main/examples/example_pngrect2masks.png" width=35% height=35%> | <img src="https://github.com/mirabarukaso/ComfyUI_Mira/blob/main/examples/example_pngrect2masks_overlap.png" width=35% height=35%>  |

------
Create Mask With Canvas      
Create a new `mask` on defined `cavans`.   
In case you need `merge` multiple `masks`, try search `MaskComposite` with `operation add`.   
    
| Inputs | Description |
| --- | --- |
| `C_Width` | Width of cavans. |
| `C_Height` | Height of cavans. |
| `X` | The left point of new mask on cavans. |
| `Y` | The top point of new mask on cavans. |
| `Width` | Mask width. |
| `Height` | Mask height. |
| `Intenisity` | `Intenisity` of Mask, set to `1.0` for solid Mask. |
| `Blur` | The intensity of blur around the edge of Mask, set to `0` for a solid edge. |
        
| Outputs | Description |
| --- | --- |
| `mask` | New mask with defined cavans |

Example   
<img src="https://github.com/mirabarukaso/ComfyUI_Mira/blob/main/examples/example_createmaskwithcavans.png" width=35% height=35%>   

------
Create Watermark Removal Mask     
Creates multiple `masks` at the corners of the image for subsequent watermark detection and removal.    
Ideas from [comfyui-lama-remover](https://github.com/Layer-norm/comfyui-lama-remover)

***Reminder: If you disable all 4 corners, the bottom right corner will be enabled by default. ***

| Inputs | Description |
| --- | --- |
| `C_Width` | Width of cavans. |
| `C_Height` | Height of cavans. |
| `Mask_W` | Mask width, maxium value are half of cavans width. |
| `Mask_H` | Mask height, maxium value are half of cavans height. |
| `Top_L` | Create mask from top left. |
| `Top_R` | Create mask from top right. |
| `Bottom_L` | Create mask from bottom left. |
| `Bottom_R` | Create mask from bottom right. |  
| `EdgeToEdge` | Preserve the N pixels at the outermost edges of the image to prevent image noise. Set to 0 for borderless. |
| `Intenisity` | `Intenisity` of Mask, set to `1.0` for solid Mask. |
| `Blur` | The intensity of blur around the edge of Mask, set to `0` for a solid edge. |
        
| Outputs | Description |
| --- | --- |
| `Mask` | New mask with defined cavans |

| ***Before*** | ***After*** |
| --- | --- |
| <img src="https://github.com/mirabarukaso/ComfyUI_Mira/blob/main/examples/example_watermark_removal_mask_before.png" width=35% height=35%> |  <img src="https://github.com/mirabarukaso/ComfyUI_Mira/blob/main/examples/example_watermark_removal_mask_after.png" width=35% height=35%> |

------
### Util
Create Canvas    
Create Canvas information `Width` and `Height` for Latent with Landscape switch. There's an advanced version also controls `Batch` and `HiResMultiplier`.

| Inputs | Description |
| --- | --- |
| Basic |
| `Width`  `Height` | Image size. |
| Normal |
| `Landscape` | Swap `Width` and `Height` by one click. |
| Advanced |
| `Batch`  | Batch size. |
| `HiResMultiplier`  | Automatically calculated (in steps of 8) for HiResFix. |

| Outputs | Description |
| --- | --- |
| Basic & Normal |
| `Width`  `Height` | Image size. Swaps automatically when `Landscape` is Enabled. |
| Advanced | 
| `Batch`  | Batch size. |
| `HiRes Width` `HiRes Height`  | Width and Height for HiResFix or etc. <br />***NOTE:The result is not the product of the original data, but the nearest multiple of 8.***|
| `HiResMultiplier`  | Same as input |

------
Random Tilling Layouts    
Random Tilling Mask `Layout` Generator for `Create Tilling PNG Mask -> Layout`   

**Highly recommend connect the output `layout` or `Create PNG Mask -> Debug` to `ShowText` node.**   
Refer to [ComfyUI-Custom-Scripts](https://github.com/pythongosssss/ComfyUI-Custom-Scripts)   

**Known Issue** about `Seed Generator`   
Switching `randomize` to `fixed` now works immediately.   
But, switching `fixed` to `randomize`, it need 2 times `Queue Prompt` to take affect. (Because of the ComfyUI logic)   
      
Solution: Try `Global Seed (Inspire)` from [ComfyUI-Inspire-Pack](https://github.com/ltdrdata/ComfyUI-Inspire-Pack)   

**Reminder**   
The `rnd_seed` have nothing to do with the actual random numbers, you can't get the same `layout` with the same `rnd_seed`, it is recommended to use `ShowText` and `Notes` to save your favourite `layout`.   

**Hint**   
Set rows or colums to `0` for only one direction cuts. Whichever is set to `0` will automatically cut according to the other non-zero setting. Just in case all fours are `0`, it will return `1,1`.   
    
| Inputs | Description |
| --- | --- |
| `min_rows` `max_rows` | Range of how many `N cuts` you may want, set both to 0 to disable it. |
| `min_colums` `max_colums` | Range of how many `G cuts` you may want, set both to 0 to disable it. |
| `max_weights_gcuts` | The maxium weight of `G cuts` range from 1 to `max_weights_gcuts` |
| `max_weights_ncuts` | The maxium weight of `N cuts` range from 1 to `max_weights_ncuts` | 
| `rnd_seed`| Connect to the `Seed Generator` node, then use `Global Seed (Inspire)` node to control it properly. |
    
| Outputs | Description |
| --- | --- |
| `Layout` | Layouts string, you need connect it to `Create PNG Mask -> layout` |

Example   
<img src="https://github.com/mirabarukaso/ComfyUI_Mira/blob/main/examples/example_random_layouts.png" width=35% height=35%>   

------
Random Nested Mask Layouts    
Random Nested Mask `Layout` Generator for `Create Nested PNG Mask -> Layout`  
    
**Known Issue** same as upper one.
    
| Inputs | Description |
| --- | --- |
| `min_nested`, `max_nested` | Range of nest you want. |
| `min_weights`, `max_weights` | The weight of every nest. |
| `rnd_seed` | Connect to the `Seed Generator` node, then use `Global Seed (Inspire)` node to control it properly. |
            
| Outputs | Description |
| --- | --- |
| `Layout` | Layouts string, you need connect it to `Create Nested PNG Mask -> layout` |
| `top`, `bottom`, `left`, `right` | Random Boolean for `Create Nested PNG Mask -> Layout` |

Example   
<img src="https://github.com/mirabarukaso/ComfyUI_Mira/blob/main/examples/example_random_nested_layouts.png" width=35% height=35%>   

------
Seed Generator    
Random `Seed` Generator for `Random Layouts`, same as normal random seed generator.   

------
### Util/Image    
Simple Image Adjustment Utilities    

All nodes can be used in a daisy chain.    

| Node | Description |
| --- | --- |
| `To Grayscale` | N/A |
| `Adjust Contrast` | 0 ~ 10 |
| `Adjust Sharpness` | 0 ~ 100  |
| `Adjust Brightness` | 0 ~ 10 |
| `Adjust Saturation` | 0 ~ 10 |
| `Adjust HUE` | -0.5 ~ 0.5 | 
| `Adjust Gamma` | 0 ~ 10 |
| `Adjust Tone Curve` | S-Curve -10 ~ 10 | 
| `RGB Channel` | 0 ~ 5 |

Example   
<img src="https://github.com/mirabarukaso/ComfyUI_Mira/blob/main/examples/example_image_adjust.png" width=35% height=35%>   

------
### Image Color Transfer      
0.4.9.8 and above Supports Images input for video color calibration          

Refer to    
https://github.com/pengbo-learn/python-color-transfer/    
https://en.wikipedia.org/wiki/Image_color_transfer    

color_transfer.py credits to pengbo-learn(GitHub)    

Special Thanks    
https://github.com/chia56028/Color-Transfer-between-Images    
https://qiita.com/hideo130/items/f4a8f340016951107646    

Image Resolution 2336 x 3488    
| Method | Speed | Time |
| --- | --- | --- |
| `mean` | Instantly | 1.768s |
| `lab` | Almost Instantly | 2.469s |
| `pdf` | Slow  | 18.096s |
| `pdf + regrain` | Go for a walk | 49.796s |

Example   
<img src="https://github.com/mirabarukaso/ComfyUI_Mira/blob/main/examples/example_color_transfer.png" width=35% height=35%>   

For Video     
|  Sample  |
| --- |
| <img src="https://github.com/mirabarukaso/ComfyUI_Mira/blob/main/examples/image_color_transfer/2025-08-24-234219_2151512547.png" width=15% height=15%>  |
|[Default result](https://github.com/mirabarukaso/ComfyUI_Mira/blob/main/examples/image_color_transfer/default.mp4) |
| [Image color transfer calibrated](https://github.com/mirabarukaso/ComfyUI_Mira/blob/main/examples/image_color_transfer/calibrated.mp4)  |


------
Upscale Image By Model Then Resize     

Upscale images with a upscale model and then resize to a specified size (a multiple of 8 in length and width).     

For example, if the input model zooms the image 4x by default and the node is set to zoom 2x, then the image will first be zoomed 4x using the model and then resized to 2x.    
    
| Inputs | Description |
| --- | --- |
| `upscale_model` | Model for upscaling |
| `image` | Source Images |
| `resize_scale` | Real resize ratio, the result will be the nearest multiple of `8` |
| `resize_method` | Resize method, `nearest`, `nearest-exact`, `bilinear`, `bicubic` |
            
| Outputs | Description |
| --- | --- |
| `image` | Output Images |

Use 2x model for fast scale and resize, 8x model for best result.   

------
Image Saver without civitai stuff    
**This is a tempoary node solution for my SAA ComfyUI API**    
I need to ensure that node is stable and not changed by update.   

Forked from https://github.com/alexopus/ComfyUI-Image-Saver    
Remove download from civitai.com and easy remix    

More detail at: https://github.com/mirabarukaso/character_select_stand_alone_app/issues/5    
For common usage, use alexopus's ComfyUI-Image-Saver.     

Comparison without and with    
<img src="https://github.com/mirabarukaso/ComfyUI_Mira/blob/main/examples/example_image_saver.png" width=35% height=35%>   

------
Reverse Image And All Images      

Reverse the order of images in a batch and concatenate the reversed images with the original batch.      

| Inputs | Description |
| --- | --- |
| `images` | Source Images |
            
| Outputs | Description |
| --- | --- |
| `rev_image` | Reversed Images |
| `all_image` | Source + Reversed Images |

------
Stack Images and Extract Last Image      

Stacks the input images with optional previous images and extracts the last image from the input images.     

| Inputs | Description |
| --- | --- |
| `images` | Source Images |
| `last_images_in` | Optional input images to prepend |

| Outputs | Description |
| --- | --- |
| `all_images` | Concatenated images (last_images_in + images, or images if last_images_in is None) |
| `last_image` | Last image from the input images |

------
Flat Color Quantization     

Refer to my [Flat Color Quantization](https://github.com/mirabarukaso/flat_color_quantization)      

*Note: The ComfyUI result is NOT the same as Gradio/Console with same settings*       
Because the `Load Image` node will convert input image once then convert to IMAGE format, that cause the input image is not the same as the original PNG. Use the following settings to get 0% result for Foxie sample image.            

```
n_colors        1024
block_size      512
temperature     3.0
spatial_scale   60
sharpen         0.0
```

------
### Text
Text Switcher    
Selects `text1` or `text2` depending on the `use_text2` and automatically adds `common_text` for output.

| Inputs | Description |
| --- | --- |
| `use_text2` | When `ENABLED`, will switch `Output` to `text2 + separator + common_text`. |
| `common_text_at_front` | When `ENABLED`, the common text is placed in front of the text (1 or 2). |
| `text1` | Default output text. |
| `text2` | Alternative text when `use_text2` is `ENABLED`. |
| `common_text`  | Common text input for quality tags and etc, leave it blank if you don't need it.. |

| Outputs | Description |
| --- | --- |
| `text`  | A combined text output. |
| `text_alt`  |  Alternative combined text output. |

Example   
<img src="https://github.com/mirabarukaso/ComfyUI_Mira/blob/main/examples/example_text_switcher.png" width=35% height=35%>   

------
Text Combiner      
Simply combine text inputs together, switch them to `input node` as you wish, then connect to `Text Switcher` or `Simple Text Box`   

| Inputs | Description |
| --- | --- |
| `text1-6` | Default output text. |

| Outputs | Description |
| --- | --- |
| `text`  | A combined text output. |

For `Text Combiner Six`, you can use my naming logic to make the whole workflow easier to understand.   

| Inputs | Description |
| --- | --- |
| `text1` | All common `prompts` for model required. e.g. `score_9, score_8_up, score_7_up, score_6_up, score_5_up, best quality, masterpiece,`|
| `text2`| Base information for what you want. e.g. camera `front view, low angle view,`, style `cyberpunk, reflection,`, location `street, outdoors,`, characters (number) `1anthro` |
| `text3` | The Charater's pose information. e.g. `smile, standing, open mouth, looking at viewer,`|
| `text4` | The Charater's race and outlook information. e.g. `anthro dragon, no pupils, cowboy shot, (4 fingers:1.2), claws, (hair slicked back:1.1),` and ` (two-tone scales, (blue scales:1.2), grey stomach scales, cyan striped, cyan hair, black sclera, gold eyes:1.1), (wet, shark dragon, shark tail, (skin-covered dragon horn:1.3), arm fins, ear fins, gills, (mohawk:0.9), sidelocks:1.1), `|
| `text5` | LoRA trigger words. |
| `text6` | Any addional informaion you want. e.g. `glowing eyes, ` |

------
Text Switcher Two/Three Ways     
Found a satisfied random number and didn't want to mess up your regional nodes too much?   
**Reminder: In case you are not use a symmetrical(`1:1:1`) Mask, do not forget your `Mask Layout`**

| Inputs | Description |
| --- | --- |
| `text1-3` | Full combined text before Regional confiton |
| `switch` | Boolean/List for how to switch outputs |
        
| Outputs | Description |
| --- | --- |
| `text1-3` | As is, but switched order |

Three ways      
| Switch | Output |
| --- | --- |
| `False` | `text1` `text2` |
| `True` |  `text2` `text1` |

Three ways      
| Switch | Output |
| --- | --- |
| 1 | 123 |
| 2 | 132 |
| 3 | 213 |
| 4 | 231 |
| 5 | 312 |
| 6 | 321 |

------
Text Loop Combiner     
Combine input text with current text into a single text array with seprator.    

| Inputs | Description |
| --- | --- |
| `text` | Text need to combine with |
| `seprator` | Seprator character or array |
| Optional: `text_in` | Text from previous Text Loop Combiner(or other text box) |
        
| Outputs | Description |
| --- | --- |
| `text_out` | Combined text |

Text Wildcard Seprator      
For someone who wants to select wildcard contents by themselves.    
Split the wildcard text (TextBox) into multiple segments according to specific characters, and select the specified segment number to output.    

| Inputs | Description |
| --- | --- |
| `text` | Input text |
| `seprator` | Seprator character or array |
| `switch` | Index of output, current limit is 20(0~19) |
        
| Outputs | Description |
| --- | --- |
| `text_out` | Selected text |

Example   
<img src="https://github.com/mirabarukaso/ComfyUI_Mira/blob/main/examples/example_text_loop_combiner_and_wildcard_seprator.png" width=35% height=35%>   

------
### Logic
Boolean    
Few `Boolean` stacks.   

| Inputs | Description |
| --- | --- |
| `bool_N` | Triggers. |
| `bool_list`  | Boolean List from `N Bool` |
| `NOT_Mode`  | Inverts the Boolean value from input to output (1->0 0->1) |

| Outputs | Description |
| --- | --- |
| `bool_N`  | Bool value. |
| `bool_list`  | Boolean List to `N Bool from List` |

Logic NOT    
Always return `not Boolean`
    
| Input | Output |
| --- | --- |
| `True` | `False` |
| `False` | `True` |

Even or Odd    
Check if a `Integer` is odd or even.   

| Input | Output |
| --- | --- |
| `Even` | `False` |
| `Odd` | `True` |

None To Zero    
Check if the `check_none` is None, then set return value to `0`.   

This is a `spoofing Node` to `mess up` with `other Nodes`. Imaging everyothers could follow this rule to create their `Custom Node`, the `ComfyUI` could be more `Logic`.   
***The extra logic calls do add a bit of system overhead, but it's Python, so who cares?***   

| Inputs | Description |
| --- | --- |
| `check_none` | `None` or `NOT None` from `74 family` |
| `ret_float` | The `float` result when `NOT None`  |
| `ret_int` | The `intenger` result when `NOT None` |

| Outputs | Description |
| --- | --- |
| `ret_float` | `AS IS` when `NOT None`, and `0` when `None`  |
| `ret_int` | `AS IS` when `NOT None`, and `0` when `None`  |
| `ret_image` | `AS IS` when `NOT None`, and `2x2 img` when `None`  |
| `none_image` | `AS IS` when `NOT None`, and `None` when `None`  |

------
Even or Odd List   
Checks whether each `digit` (decimal) of the input `integer` is odd or even, and returns `true` for even numbers and `false` for odd numbers.    
The final output is a `Boolean List` which is connected to the `Boolean List Interpreter`.    
If the input `Number of digits` is less than the `Requirement`, it will go back to the lowest digit to re-recognize and complete the list,    
and the way the list is completed can be chosen as `as is` or `not`.    
The output node `String` displays the actual results.   

| Inputs | Description |
| --- | --- |
| `integer` | Recommend connect to `Seed Generator` |
| `quantity` | Length of the `Boolean list`, if `quantity` is greater than `len(str(integer))`, will trigger `filling` for extra bits.|
| `NOT_filling` | Filling algorithm, `Enable` for switch between `NOT` and `AS IS` in future loop, `Disable` for `AS IS` in every loop. |

| Outputs | Description |
| --- | --- |
| `bool_list` | Boolean list |
| `result` | String result |

Example   
<img src="https://github.com/mirabarukaso/ComfyUI_Mira/blob/main/examples/example_evenoroddlist.png" width=35% height=35%>   

------
Function Swap    
Swap `func1` and `func2` outputs depends on `trigger`.

**UPDATE!!!**
Now `func2` is `optional`, if `NOT connected` or `function bypassed`, both `Outputs` will return `func1`.    
    
| Inputs | Description |
| --- | --- |
| `swap` | `True` or `False` |
| `func1` | Any function. E.g. `Mask_1`. |
| `func2` |  Any function. E.g. `Mask_2`. |
    
| Outputs | A | B |
| --- | --- | --- |
| swap  |   A   |   B   |
| `True`  | func2 | func1 |
| `False` | func1 | func2 |

------
Function Select Auto    
Automatically select `func1` or `func2` outputs depends on which one is `NOT None`.   
Supports `ANY(*)` inputs, `func1` has higher priority.   
    
| Inputs | Description |
| --- | --- |
| `func1` | Any function. E.g. `Image from Model Image Upscaler `. |
| `func2` | Any function. E.g. `Image from Vae Decode`. |
    
| Outputs | A | B |
| --- | --- | --- |
|   Y   |   func1   |   func2   |
| None  |   None    |   None    |
| func1 |   func1   |   None    |
| func1 |   func1   |   func2   |
| func2 |   None    |   func2   |

Example   
<img src="https://github.com/mirabarukaso/ComfyUI_Mira/blob/main/examples/example_function_select_auto.png" width=35% height=35%>   

------
### Logic-74
In case you didn't know about `74 family`, refer to [List of 7400-series integrated circuits](https://en.wikipedia.org/wiki/List_of_7400-series_integrated_circuits)   

SN74LVC1G125    
Single Bus Buffer Gate With Enable   
    
|  OE   |  A   |
| --- | --- |
| True  |  Y   |
| False | None |

SN74HC1G86    
Single 2-Input Exclusive-OR(XOR) Gate    

SN74HC86    
Quadruple 2-Input Exclusive-OR(XOR) Gates   
    
|   A   |   B   |   Y  |
| --- | --- | --- |
| True  | True  | None |
| False | False | None |
| True  | False |  A   |
| False | True  |  B   |

Example   
<img src="https://github.com/mirabarukaso/ComfyUI_Mira/blob/main/examples/example_SN74HC86.png" width=35% height=35%>   

------
### Numeral
Convert Numeral to String    
Convert `Integer` or `Float` to String.   

Floats
And, few `Float` stacks.   

| Inputs | Description |
| --- | --- |
| `float_N` | Triggers. |
| `float_list`  | Float List from `N Float` |

| Outputs | Description |
| --- | --- |
| `float_N`  | Float value. |
| `float_list`  | Float List to `N Float from List` |

------
### Arithmetic (WIP as I need......)
Addition, Subtraction, Multiplication and Division.   

**Multiplier now renamed to Arithmetic.**

Multiplication    
`Integer` and `Float` Multiplier with various output interfaces.   
There is also an `Integer to Float` Multiplier, connect to `Seed Generator` (x0.1) for `Even or Odd` and `Text Switcher`.

| Inputs | Description |
| --- | --- |
| `int_value` `float_value` | The number you want to multiply. |
| `multiply_value` | How many times? |

| Outputs | Description |
| --- | --- |
| `Integer`  | `Integer` result. ***When converting `Floating` to `Integer`, the fractional part are discarded.***|
| `Float`  | `Float` result. |
| `String`  | Convert result to `String`. |

------
Subtraction    
`Integer` Subtraction with various output interfaces.   

**Mostly usage for `Create Mask With Cavans`, connect `Y` with `Result` then connect `height` with `subtracted_value`.**

| Inputs | Description |
| --- | --- |
| `int_value` | Subtracted number. |
| `subtracted_value` | Subtracted by how much? |

| Outputs | Description |
| --- | --- |
| `Integer`  | `Integer` result. |
| `String`  | Convert result to `String`. |
| `subtracted_value` | As is |

Example   
<img src="https://github.com/mirabarukaso/ComfyUI_Mira/blob/main/examples/example_subtraction.png" width=35% height=35%>   

------
### LoRA
LoRA Loader With Name Stacker    

A simple LoRA loader with name stacker for any website that could not identify all LoRAs' information from image.   
Apparently that only happens with ComfyUI...    

| Inputs | Description |
| --- | --- |
| `model`  | Your Model node, the `purple` one. |
| `clip`  | Your Clip node, the `lemon yellow` one. |
| `lora_name`  | Selected LoRA. |
| `strength_model`  | LoRA strength for Model. |
| `strength_clip`  |  LoRA strength for Clip. |
| `bypass`  | Bypass current LoRA. |

| Optional Input | Description |
| --- | --- |
| `lora_stack`  | A `STRING` array from previous `LoRA Loader With Name Stacker`.  |

***Reminder: leave the locomotive(first one) empty.***

| Outputs | Description |
| --- | --- |
| `MODEL`  | Model |
| `CLIP`  | CLIP |
| `lora_stack`  | New `STRING` array with current LoRA name and strength information. AS is when `bypass` is `Enable` or `strengths` are all `0`. |

***Reminder: For the 2nd Hires fix, the same LoRA name will be ignored.*** 

LoRA from Text

This is a blend node that extracts and blends the LoRA information you enter in webui format into the model, as well as the clip.    

Format support:
```
<lora:loraname>
<lora:loraname:model str>
<lora:loraname:model str:clip str>
<lora:loraname:model str:clip str:hires model str:hires clip str>

To bypass current LoRA in 1st or 2nd stage, set model and clip str both to 0.  
<lora:loraname:0:0:1:1>     Only works in 2nd
<lora:loraname:1:1:0:0>     Only works in 1st
<lora:loraname:0:0:0:0>     Works, but WHY??? Just delete it.
```

Prompt Example:    
```
solo, masterpiece, best quality, amazing quality,
<lora:il\[IL]Suurin2-20241120-0214.safetensors:1> suurin
```
| Inputs | Description |
| --- | --- |
| `model`  | From your Model node. |
| `clip`  | From your Clip node. |
| `text`  | Text prompt with lora and trigger words. |

| Outputs | Description |
| --- | --- |
| `model`  | LoRA strength for Model. |
| `clip`  |  LoRA strength for Clip. |
| `model_to_hifix`  | LoRA strength for 2nd Model. |
| `clip_to_hifix`  |  LoRA strength for 2nd Clip(optional). |
| `plain_text`  | Text without LoRA info, connect to CLIP Text Encoder. |

------
### Tagger  
Supports [CL Tagger@cella110n](https://huggingface.co/cella110n) and [Camie Tagger@Camais03](https://huggingface.co/Camais03)         

All taggers support single or multiple image input. In the case of multiple image input, tags will be separated by a new line for each image.                

Download CL/Camie Tagger Model and JSON file put in your `ComfyUI/model/onnx` foler.      
Rename `model.onnx` and `tag_mapping.json` with following format:      

```
ComfyUI
|---models
|   |---onnx
|       |---cl_tagger
|       |   |---cl_tagger_1_02.onnx
|       |   |---cl_tagger_1_02_tag_mapping.json
|       |---camie_tagger
|           |---camie-tagger-v2.onnx
|           |---camie-tagger-v2-metadata.json
|       |---wd_tagger
|           |---wd-eva02-large-tagger-v3.onnx
|           |---wd-eva02-large-tagger-v3_selected_tags.csv
|           |---wd-vit-large-tagger-v3.onnx
|           |---wd-vit-large-tagger-v3_selected_tags.csv
```

CL Tagger       
| Inputs | Description |
| --- | --- |
| `image`  | Image for tagger. |
| `model_name`  | Onnx model. |
| `general`  | General threshold. |
| `character`  | Character threshold. |
| `replace_space`  | Replace '_' with ' ' (space). |
| `categories`  | Selected categories in generate tags, and order by input order. |
| `session`  | Tagger Model in CPU or GPU session. Release will release session after generate. |
| `exclude_tags`  | Exclude tags. |

Camie Tagger     
| Inputs | Description |
| --- | --- |
| `image`  | Image for tagger. |
| `model_name`  | Onnx model. |
| `general`  | General threshold. |
| `min_confidence`  | Minimum confidence to display. |
| `replace_space`  | Replace '_' with ' ' (space). |
| `categories`  | Selected categories in generate tags, and order by input order. |
| `session`  | Tagger Model in CPU or GPU session. Release will release session after generate. |
| `exclude_tags`  | Exclude tags. |

WD Tagger     
| Inputs | Description |
| --- | --- |
| `image`  | Image for tagger. |
| `model_name`  | Onnx model. |
| `general_threshold`  | General threshold. |
| `character_threshold`  | Character threshold. |
| `general_mcut`  | Use mCut for General tags. |
| `character_mcut`  | Use mCut for Character tags. |
| `replace_space`  | Replace '_' with ' ' (space). |
| `categories`  | Selected categories in generate tags. |
| `session`  | Tagger Model in CPU or GPU session. Release will release session after generate. |
| `exclude_tags`  | Exclude tags. |

| Output | Description |
| --- | --- |
| `tags`  | Generated tags. |

Example     
<img src="https://github.com/mirabarukaso/ComfyUI_Mira/blob/main/examples/tagger.png" width=35% height=35%>   

------
### WAI illustrious Character Select    
ComfyUI version of [character_select_stand_alone_app](https://github.com/mirabarukaso/character_select_stand_alone_app)    

You can manually delete `mira/json/wai_character_thumbs.json`, and you can also delete `wai_characters.csv` for new Character List download           
If you really need those thumbnail    
Try [character_select_stand_alone_app](https://github.com/mirabarukaso/character_select_stand_alone_app)     
And, Online Character Select Simple Advanced App [Hugging Face Space](https://huggingface.co/spaces/flagrantia/character_select_saa)       

To use Remote `AI Promor Generator`, you need add your private `API KEY` to `custom_nodes/ComfyUI_Mira/json/settings.json`    

Example     
<img src="https://github.com/mirabarukaso/ComfyUI_Mira/blob/main/examples/example_wai_character_selecter.png" width=35% height=35%>   

------
## Overview - Regional Conditioning Mask with HiRes Fix
   
Illustrious XL    
Reminder: Due to ComfyUI update this example may outdated.    

<img src="https://github.com/mirabarukaso/ComfyUI_Mira/blob/main/examples/overview01.png" width=50% height=50%>

------

## Latest Change Log   
#### 2025.05.05 Ver 0.4.9.5    
・Add `character_weight` & `insert_before_character` for `Character Select` nodes        


