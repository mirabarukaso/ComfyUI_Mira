cat = "Mira/Text"

class TextBox:
    '''
    A simple TextBox.
    '''
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {
                    "multiline": True, 
                }),
            },
        }
                
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "TextBoxEx"
    CATEGORY = cat
    
    def TextBoxEx(self, text):
        return (text,)

class TextWithBooleanSwitchAndCommonTextInput:
    '''
    Selects Text 1 or Text 2 depending on the switch and automatically adds Common Text for output.
    
    Inputs:
    use_text2               - When ENABLED, will switch output to text2 + separator + common_text
    common_text_at_front    - When ENABLED, the common text is placed in front of the text (1 or 2).
    text1                   - Default output text
    text2                   - Alternative text when use_text2 is ENABLED
    common_text             - Common text input for quality tags and etc, leave it blank if you don't need it.
        
    Outputs:
    text                    - Combined text output   
    text_alt                - Alternative combined text output    
    '''
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "use_text2": ("BOOLEAN", {
                    "default": False,
                    "display": "input"
                }),
                "common_text_at_front": ("BOOLEAN", {
                    "default": False,
                    "display": "input"
                }),
                "text1": ("STRING", {
                    "multiline": True, 
                }),
                "text2": ("STRING", {
                    "multiline": True, 
                }),
                "common_text": ("STRING", {
                    "multiline": True, 
                    "display": "input"
                }),
            },
        }
                
    RETURN_TYPES = ("STRING", "STRING",)
    RETURN_NAMES = ("text","alt_text",)
    FUNCTION = "TextWithBooleanSwitchAndCommonTextInputEx"
    CATEGORY = cat
    
    def TextWithBooleanSwitchAndCommonTextInputEx(self, use_text2, common_text_at_front, text1, text2, common_text):
        if True == common_text_at_front:
            if True == use_text2:
                return (common_text + text2, common_text + text1,)
            else:
                return (common_text + text1, common_text + text2,)
        else:
            if True == use_text2:
                return (text2 + common_text, text1 + common_text,)
            else:
                return (text1 + common_text, text2 + common_text,)

class TextCombinerSix:
    '''
    Simply combine six input texts for regional text
    
    Inputs:
    text1-6     - Input text
        
    Outputs:
    text        - A combined text output    
    '''
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text1": ("STRING", {"display": "input"}),
                "text2": ("STRING", {"display": "input"}),
                "text3": ("STRING", {"display": "input"}),
                "text4": ("STRING", {"display": "input"}),
                "text5": ("STRING", {"display": "input"}),
                "text6": ("STRING", {"display": "input"}),
            },
        }
                
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "TextCombinerSixEx"
    CATEGORY = cat
    
    def TextCombinerSixEx(self, text1, text2, text3, text4, text5, text6):
        return (text1 + text2 + text3 + text4 + text5 + text6,)
    
class TextCombinerTwo:
    '''
    Simply combine two input texts for regional text
    
    Inputs:
    text1-2     - Input text
        
    Outputs:
    text        - A combined text output    
    '''
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text1": ("STRING", {"display": "input"}),
                "text2": ("STRING", {"display": "input"}),
            },
        }
                
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "TextCombinerTwoEx"
    CATEGORY = cat
    
    def TextCombinerTwoEx(self, text1, text2):
        return (text1 + text2,)

class TextSwitcherTwoWays:
    '''
    Text Switcher Two Ways
    In face that's for my Mask Layouts
    
    Inputs:
    text1        - Input text1
    text2        - Input text2    
    switch       - When ENABLED, will switch output as `text2` and `text1`
        
    Outputs:
    text         - As is text1 or text 2
    textA        - As is text1 or text 2    
      
    | Switch | Output      |
    | False  | text1 text2 |
    | True   | text2 text1 |
    '''
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text1": ("STRING", {"display": "input"}),
                "text2": ("STRING", {"display": "input"}),
                "switch": ("BOOLEAN", {"default": False,}),      
            },
        }
                
    RETURN_TYPES = ("STRING","STRING",)
    RETURN_NAMES = ("text1","text2",)
    FUNCTION = "TextSwitcherTwoWaysEx"
    CATEGORY = cat
    
    def TextSwitcherTwoWaysEx(self, text1, text2, switch):
        if True is switch:
            return (text2, text1,)
    
        return (text1, text2,)
        
class TextSwitcherThreeWays:
    '''
    Text Switcher Three Ways
    Found a satisfied random number and didn't want to mess up your regional nodes too much?
    
    Inputs:
    text1        - Input text1
    text2        - Input text2    
    text3        - Input text3
    switch       - List for how to switch 123
        
    Outputs:
    text1        - text1
    text2        - text2    
    text3        - text3
      
    | S | Out |
    | 1 | 123 |
    | 2 | 132 |
    | 3 | 213 |
    | 4 | 231 |
    | 5 | 312 |
    | 6 | 321 |
    '''
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text1": ("STRING", {"display": "input"}),
                "text2": ("STRING", {"display": "input"}),
                "text3": ("STRING", {"display": "input"}),           
                "switch": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 6,
                    "step": 1,
                    "display": "slider" 
                }),        
            },
        }
                
    RETURN_TYPES = ("STRING","STRING","STRING",)
    RETURN_NAMES = ("text1","text2","text3",)
    FUNCTION = "TextSwitcherThreeWaysEx"
    CATEGORY = cat
    
    def TextSwitcherThreeWaysEx(self, text1, text2, text3, switch):
        match switch:
            case 1: #123
                return (text1, text2, text3,)
            case 2: #132
                return (text1, text3, text2,)
            case 3: #213
                return (text2, text1, text3,)
            case 4: #231
                return (text2, text3, text1,)
            case 5: #312
                return (text3, text1, text2,)
            case 6: #321
                return (text3, text2, text1,)
    
        return (text1, text2, text3,)