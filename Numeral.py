cat = "Mira/Numeral"

class AlwaysEqualProxy(str):
#ComfyUI-Logic 
#refer: https://github.com/theUpsider/ComfyUI-Logic
    def __eq__(self, _):
        return True

    def __ne__(self, _):
        return False
    
class NumeralToString:
    '''
    Convert Integer or Float to String.   
    
    Inputs:
    numeral     - Integer or Float number
        
    Outputs:
    text        - String output
    '''
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "numeral": (AlwaysEqualProxy('*'), {
                    "default": 0.0,
                    "display": "input" 
                }),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("Result (STRING)",)
    FUNCTION = "execute"
    CATEGORY = cat

    def execute(self, numeral):
        if type(numeral) is int or type(numeral) is float:
            return (str(numeral),)
        else:
            result = 'Mira: invalid input Type '
            result += str(type(numeral))
            return (result,)
        

class TwoFloats:
    '''
    2 Floats
    '''
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "float_1": ("FLOAT", {"default": 1.0, "step": 0.1}),
                "float_2": ("FLOAT", {"default": 1.0, "step": 0.1}),
            },
        }
                
    RETURN_TYPES = ("FLOAT","FLOAT",)
    RETURN_NAMES = ("float_1","float_2",)
    FUNCTION = "TwoFloatsEx"
    CATEGORY = cat
    
    def TwoFloatsEx(self, float_1, float_2,):
        return (float_1, float_2,)
class FourFloats:
    '''
    4 Floats
    '''
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "float_1": ("FLOAT", {"default": 1.0, "step": 0.1}),
                "float_2": ("FLOAT", {"default": 1.0, "step": 0.1}),
                "float_3": ("FLOAT", {"default": 1.0, "step": 0.1}),
                "float_4": ("FLOAT", {"default": 1.0, "step": 0.1}),
            },
        }
                
    RETURN_TYPES = ("FLOAT","FLOAT","FLOAT","FLOAT",)
    RETURN_NAMES = ("float_1","float_2","float_3","float_4",)
    FUNCTION = "FourFloatsEx"
    CATEGORY = cat
    
    def FourFloatsEx(self, float_1, float_2, float_3, float_4):
        return (float_1, float_2, float_3, float_4, )

class SixFloats:
    '''
    6 Floats
    '''
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "float_1": ("FLOAT", {"default": 1.0, "step": 0.1}),
                "float_2": ("FLOAT", {"default": 1.0, "step": 0.1}),
                "float_3": ("FLOAT", {"default": 1.0, "step": 0.1}),
                "float_4": ("FLOAT", {"default": 1.0, "step": 0.1}),
                "float_5": ("FLOAT", {"default": 1.0, "step": 0.1}),
                "float_6": ("FLOAT", {"default": 1.0, "step": 0.1}),
            },
        }
                
    RETURN_TYPES = ("FLOAT","FLOAT","FLOAT","FLOAT","FLOAT","FLOAT",)
    RETURN_NAMES = ("float_1","float_2","float_3","float_4","float_5","float_6",)
    FUNCTION = "SixFloatsEx"
    CATEGORY = cat
    
    def SixFloatsEx(self, float_1, float_2, float_3, float_4, float_5, float_6):
        return (float_1, float_2, float_3, float_4, float_5, float_6,)
    