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
        
class OneFloat:
    '''
    1 Float
    '''
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "float_1": ("FLOAT", {"default": 1.0, "step": 0.01}),
            },
        }
                
    RETURN_TYPES = ("FLOAT",)
    RETURN_NAMES = ("float_1",)
    FUNCTION = "OneFloatEx"
    CATEGORY = cat
    
    def OneFloatEx(self, float_1, ):
        return (float_1, )

class TwoFloats:
    '''
    2 Floats
    '''
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "float_1": ("FLOAT", {"default": 1.0, "step": 0.01, "min": -10.0, "max":10.0}),
                "float_2": ("FLOAT", {"default": 1.0, "step": 0.01, "min": -10.0, "max":10.0}),
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
                "float_1": ("FLOAT", {"default": 1.0, "step": 0.01, "min": -10.0, "max":10.0}),
                "float_2": ("FLOAT", {"default": 1.0, "step": 0.01, "min": -10.0, "max":10.0}),
                "float_3": ("FLOAT", {"default": 1.0, "step": 0.01, "min": -10.0, "max":10.0}),
                "float_4": ("FLOAT", {"default": 1.0, "step": 0.01, "min": -10.0, "max":10.0}),
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
                "float_1": ("FLOAT", {"default": 1.0, "step": 0.01, "min": -10.0, "max":10.0}),
                "float_2": ("FLOAT", {"default": 1.0, "step": 0.01, "min": -10.0, "max":10.0}),
                "float_3": ("FLOAT", {"default": 1.0, "step": 0.01, "min": -10.0, "max":10.0}),
                "float_4": ("FLOAT", {"default": 1.0, "step": 0.01, "min": -10.0, "max":10.0}),
                "float_5": ("FLOAT", {"default": 1.0, "step": 0.01, "min": -10.0, "max":10.0}),
                "float_6": ("FLOAT", {"default": 1.0, "step": 0.01, "min": -10.0, "max":10.0}),
            },
        }
                
    RETURN_TYPES = ("FLOAT","FLOAT","FLOAT","FLOAT","FLOAT","FLOAT",)
    RETURN_NAMES = ("float_1","float_2","float_3","float_4","float_5","float_6",)
    FUNCTION = "SixFloatsEx"
    CATEGORY = cat
    
    def SixFloatsEx(self, float_1, float_2, float_3, float_4, float_5, float_6):
        return (float_1, float_2, float_3, float_4, float_5, float_6,)
    
class EightFloats:
    '''
    8 Floats
    '''
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "float_1": ("FLOAT", {"default": 1.0, "step": 0.01, "min": -10.0, "max":10.0}),
                "float_2": ("FLOAT", {"default": 1.0, "step": 0.01, "min": -10.0, "max":10.0}),
                "float_3": ("FLOAT", {"default": 1.0, "step": 0.01, "min": -10.0, "max":10.0}),
                "float_4": ("FLOAT", {"default": 1.0, "step": 0.01, "min": -10.0, "max":10.0}),
                "float_5": ("FLOAT", {"default": 1.0, "step": 0.01, "min": -10.0, "max":10.0}),
                "float_6": ("FLOAT", {"default": 1.0, "step": 0.01, "min": -10.0, "max":10.0}),
                "float_7": ("FLOAT", {"default": 1.0, "step": 0.01, "min": -10.0, "max":10.0}),
                "float_8": ("FLOAT", {"default": 1.0, "step": 0.01, "min": -10.0, "max":10.0}),
            },
        }
                
    RETURN_TYPES = ("FLOAT","FLOAT","FLOAT","FLOAT","FLOAT","FLOAT","FLOAT","FLOAT",)
    RETURN_NAMES = ("float_1","float_2","float_3","float_4","float_5","float_6","float_7","float_8",)
    FUNCTION = "SixFloatsEx"
    CATEGORY = cat
    
    def SixFloatsEx(self, float_1, float_2, float_3, float_4, float_5, float_6, float_7, float_8):
        return (float_1, float_2, float_3, float_4, float_5, float_6, float_7, float_8,)
    
class StepsAndCfg:
    '''
    Steps and CFG
    '''
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "steps": ("INT", {"default": 22, "step": 1, "min": 1}),
                "cfg": ("FLOAT", {"default": 8.0, "step": 0.1, "min": 1.0}),
            },
        }
                
    RETURN_TYPES = ("INT", "FLOAT",)
    RETURN_NAMES = ("STEPS", "CFG",)
    FUNCTION = "StepsAndCFGEx"
    CATEGORY = cat
    
    def StepsAndCFGEx(self, steps, cfg):
        return (steps, cfg,)
    
class StepsAndCfgAndWH:
    '''
    Steps and CFG and Width and Height
    '''
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "steps": ("INT", {"default": 22, "step": 1, "min": 1}),
                "cfg": ("FLOAT", {"default": 8.0, "step": 0.1, "min": 1.0}),
                "width": ("INT", {
                    "default": 576,
                    "min": 16,
                    "step": 8,
                    "display": "number" 
                }),
                "height": ("INT", {
                    "default": 1024,
                    "min": 16,
                    "step": 8,
                    "display": "number" 
                }),
            },
        }
                
    RETURN_TYPES = ("INT", "FLOAT", "INT", "INT",)
    RETURN_NAMES = ("STEPS", "CFG", "Width", "Height",)
    FUNCTION = "StepsAndCfgAndWHEx"
    CATEGORY = cat
    
    def StepsAndCfgAndWHEx(self, steps, cfg, width, height):
        return (steps, cfg, width, height,)
    
    