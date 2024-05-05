cat = "Mira/Numeral"

def FloatListInterpreter(float_list, Start_At_Index, times = 1):
    new_list = []
    index = Start_At_Index
    list_len = len(float_list)
    
    for _ in range(times):
        if index >= list_len:
            index = 0
            
        new_float = float_list[index]
        new_list.append(new_float)      
        index = index + 1
        
    return (new_list)              


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
                "float_1": ("FLOAT", {"default": 1.0, "step": 0.0001}),
                "float_2": ("FLOAT", {"default": 1.0, "step": 0.0001}),
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
                
    RETURN_TYPES = ("FLOAT_LIST",)
    RETURN_NAMES = ("float_list",)
    FUNCTION = "FourFloatsEx"
    CATEGORY = cat
    
    def FourFloatsEx(self, float_1, float_2, float_3, float_4):
        float_list = [float_1, float_2, float_3, float_4,]
        return (float_list,)

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
                
    RETURN_TYPES = ("FLOAT_LIST",)
    RETURN_NAMES = ("float_list",)
    FUNCTION = "EightFloatsEx"
    CATEGORY = cat
    
    def EightFloatsEx(self, float_1, float_2, float_3, float_4, float_5, float_6, float_7, float_8):
        float_list = [float_1, float_2, float_3, float_4, float_5, float_6, float_7, float_8]
        return (float_list,)

class FloatListInterpreter1:  
    '''   
    Decode `Float` value(s) from `Float list`.
    
    Inputs:
    float_list      - Float list
    Start_At_Index  - If `Start_At_Index` is greater than length of `Float list`, it will restart from `0`
    
    Outputs:
    float(0~N)      - Float list    
    '''
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "float_list": ("FLOAT_LIST", {
                    "display": "input", 
                }),
                "Start_At_Index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "step": 1,
                    "display": "number" 
                }),                
            },            
        }
        
    RETURN_TYPES = ("FLOAT", )
    RETURN_NAMES = ("float", )
    FUNCTION = "FloatListInterpreter1Ex"
    CATEGORY = cat
    
    def FloatListInterpreter1Ex(self, float_list, Start_At_Index):
        new_list = FloatListInterpreter(float_list, Start_At_Index)
            
        return (new_list[0],)
class FloatListInterpreter4:  
    '''   
    Same as FloatListInterpreter1
    '''
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "float_list": ("FLOAT_LIST", {
                    "display": "input", 
                }),
                "Start_At_Index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "step": 1,
                    "display": "number" 
                }),                
            },            
        }
        
    RETURN_TYPES = ("FLOAT", "FLOAT", "FLOAT", "FLOAT",)
    RETURN_NAMES = ("float_1", "float_2", "float_3", "float_4", )
    FUNCTION = "FloatListInterpreter4Ex"
    CATEGORY = cat
    
    def FloatListInterpreter4Ex(self, float_list, Start_At_Index):
        new_list = FloatListInterpreter(float_list, Start_At_Index, 4)
            
        return (new_list[0],new_list[1],new_list[2],new_list[3],)
    
class FloatListInterpreter8:  
    '''   
    Same as FloatListInterpreter1
    '''
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "float_list": ("FLOAT_LIST", {
                    "display": "input", 
                }),
                "Start_At_Index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "step": 1,
                    "display": "number" 
                }),                
            },            
        }
        
    RETURN_TYPES = ("FLOAT", "FLOAT", "FLOAT", "FLOAT","FLOAT", "FLOAT", "FLOAT", "FLOAT",)
    RETURN_NAMES = ("float_1", "float_2", "float_3", "float_4", "float_5", "float_6", "float_7", "float_8",)
    FUNCTION = "FloatListInterpreter8Ex"
    CATEGORY = cat
    
    def FloatListInterpreter8Ex(self, float_list, Start_At_Index):
        new_list = FloatListInterpreter(float_list, Start_At_Index, 8)
            
        return (new_list[0],new_list[1],new_list[2],new_list[3],new_list[4],new_list[5],new_list[6],new_list[7],)
    
class StepsAndCfg:
    '''
    Steps and CFG
    '''
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "steps": ("INT", {"default": 22, "step": 1, "min": 1}),
                "cfg": ("FLOAT", {"default": 8.0, "step": 0.01, "min": 1.0}),
            },
        }
                
    RETURN_TYPES = ("INT", "FLOAT",)
    RETURN_NAMES = ("STEPS", "CFG",)
    FUNCTION = "StepsAndCFGEx"
    CATEGORY = cat
    
    def StepsAndCFGEx(self, steps, cfg):
        return (steps, cfg,)
    

