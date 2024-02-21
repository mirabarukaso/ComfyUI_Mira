# ComfyUI_Mira
A custom node for [ComfyUI](https://github.com/comfyanonymous/ComfyUI/) to improve all those custom nodes I feel not comfortable in my workflow.

------

## Installation
`Clone` the repository to custom_nodes in your `ComfyUI\custom_nodes` directory:
```
git clone https://github.com/mirabarukaso/ComfyUI_Mira.git
```

------

## Basic Functions   
### Mira/Mask/Create PNG Mask 
Create a PNG tiled image with Color Mask stack for regional conditioning mask.   
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
| `PngColorMasks` | A List contains all your Blocks' color information.  <br />Connect to `Color Mask to HEX String` `Color Mask to INT RGB` `Color Masks List` |
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
### Mira/Mask/Create PNG Mask 
Convert ranged `PngColorMasks` to Masks with(or without) Blur. **Dunno if there is a proper way to solve the output problem.**

| Inputs | Description |
| --- | --- |
| `Image` | Image from ` Mira/Mask/Create PNG Mask` |
| `PngColorMasks` | List from ` Mira/Mask/Create PNG Mask` |
| `Blur` | The first block index number you want. |
| `Start_At_Index` | The first block index number you want. |

| Outputs | Description |
| --- | --- |
| `mask_[0-9]` | The Mask for `Regional Conditioning By Color Mask (Inspire)` or etc. |

| ***Solid*** | ***Blur 16.0*** |
| --- | --- |
| <img src="https://github.com/mirabarukaso/ComfyUI_Mira/blob/main/examples/example_mask2mask_solid.png" width=35% height=35%> | <img src="https://github.com/mirabarukaso/ComfyUI_Mira/blob/main/examples/example_mask2mask_blur.png" width=35% height=35%> |

------
### Mira/Mask/Color Mask to HEX String
Convert specified `Index` `PngColorMasks` to HEX value. e.g. `RGB(255,0,255)` to `#FF00FF`

| Inputs | Description |
| --- | --- |
| `PngColorMasks` | List from ` Mira/Mask/Create PNG Mask` |
| `Index` | The block index number. |

| Outputs | Description |
| --- | --- |
| `mask_color` | The color RGB in HEX for `Regional Conditioning By Color Mask (Inspire)` or etc. |

------
### Mira/Mask/Color Mask to INT RGB
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
### Mira/Mask/Color Masks to List
Convert ranged `PngColorMasks` to HEX value. **Dunno if there is a proper way to solve the output problem.**

| Inputs | Description |
| --- | --- |
| `PngColorMasks` | List from ` Mira/Mask/Create PNG Mask` |
| `Start_At_Index` | The first block index number you want. |

| Outputs | Description |
| --- | --- |
| `mask_color_[0-9]` | The color RGB in HEX for `Regional Conditioning By Color Mask (Inspire)` or etc. |

------
### Mira/Util/Create Canvas
Create Canvas information `Width` and `Height` for Latent with Landscape switch. There's an advanced version also controls `Batch` and `HiResMultiplier`.

| Inputs | Description |
| --- | --- |
| `Width`  `Height` | Image size. |
| `Landscape` | Swap `Width` and `Height` by one click. |
| Advanced | --- |
| `Batch`  | Batch size. |
| `HiResMultiplier`  | Automatically calculated (in steps of 8) for HiResFix. |
| `Debug` | Debug information as String. |

| Outputs | Description |
| --- | --- |
| `Width`  `Height` | Image size. Swaps automatically when `Landscape` is Enabled. |
| Advanced | --- |
| `Batch`  | Batch size. |
| `HiRes Width` `HiRes Height`  | Width and Height for HiResFix or etc. |

------
### Mira/Numeral/Convert Numeral to String
Convert `Integer` or `Float` to String.   

------
### Mira/Multiplier
`Integer` and `Float` Multiplier with various output interfaces.

| Inputs | Description |
| --- | --- |
| `input_value` | The number you want tu multiply. |
| `multiply_value` | How many times? |

| Outputs | Description |
| --- | --- |
| `Integer`  | `Integer` result. ***When converting `Floating` to `Integer`, the fractional part are discarded.***|
| `Float`  | `Float` result. |
| `String`  | Convert result to `String`. |

------

## Change Logs
### 2024.02.21 Ver 0.3.0.0
・Initial release
