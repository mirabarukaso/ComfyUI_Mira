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
    use_text2   - When ENABLED, will switch output to text2 + separator + common_text
    text1       - Default output text
    text2       - Alternative text when use_text2 is ENABLED
    separator   - Separator between text(1/2) and common_text, default value is ","
    common_text - Common text input for quality tags and etc, leave it blank if you don't need it.
        
    Outputs:
    text        - A combined text output    
    '''
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "use_text2": ("BOOLEAN", {
                    "default": False,
                    "display": "input"
                }),
                "text1": ("STRING", {
                    "multiline": True, 
                }),
                "text2": ("STRING", {
                    "multiline": True, 
                }),
                "separator": ("STRING", {
                    "multiline": False, 
                    "default": ","
                }),
                "common_text": ("STRING", {
                    "multiline": True, 
                    "display": "input"
                }),
            },
        }
                
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "TextWithBooleanSwitchAndCommonTextInputEx"
    CATEGORY = cat
    
    def TextWithBooleanSwitchAndCommonTextInputEx(self, use_text2, text1, text2, separator, common_text):
        if True == use_text2:
            return (text2 + separator + common_text,)
        else:
            return (text1 + separator + common_text,)

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