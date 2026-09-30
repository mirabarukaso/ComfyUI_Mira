from comfy_api.latest import IO
from .v3schema import node

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
    
class NumeralToString(IO.ComfyNode):
    '''
    Convert Integer or Float to String.   
    
    Inputs:
    numeral     - Integer or Float number
        
    Outputs:
    text        - String output
    '''
    @classmethod
    def define_schema(cls):
        return node(
            "NumeralToString",
            cat,
            cls._v1_inputs(),
            ("STRING",),
            ("Result (STRING)",),
        )

    @classmethod
    def _v1_inputs(s):
        return {
            "required": {
                "numeral": (AlwaysEqualProxy('*'), {
                    "default": 0.0,
                    "display": "input" 
                }),
            },
        }


    @classmethod
    def execute(cls, numeral):
        if type(numeral) is int or type(numeral) is float:
            return (str(numeral),)
        else:
            result = 'Mira: invalid input Type '
            result += str(type(numeral))
            return (result,)
        
class OneFloat(IO.ComfyNode):
    '''
    1 Float
    '''
    @classmethod
    def define_schema(cls):
        return node(
            "OneFloat",
            cat,
            cls._v1_inputs(),
            ("FLOAT",),
            ("float_1",),
        )

    @classmethod
    def _v1_inputs(s):
        return {
            "required": {
                "float_1": ("FLOAT", {"default": 1.0, "step": 0.01}),
            },
        }
                
    
    @classmethod
    def execute(cls, float_1, ):
        return (float_1, )

class TwoFloats(IO.ComfyNode):
    '''
    2 Floats
    '''
    @classmethod
    def define_schema(cls):
        return node(
            "TwoFloats",
            cat,
            cls._v1_inputs(),
            ("FLOAT","FLOAT",),
            ("float_1","float_2",),
        )

    @classmethod
    def _v1_inputs(s):
        return {
            "required": {
                "float_1": ("FLOAT", {"default": 1.0, "step": 0.0001}),
                "float_2": ("FLOAT", {"default": 1.0, "step": 0.0001}),
            },
        }
                
    
    @classmethod
    def execute(cls, float_1, float_2,):
        return (float_1, float_2,)
    
class FourFloats(IO.ComfyNode):
    '''
    4 Floats
    '''
    @classmethod
    def define_schema(cls):
        return node(
            "FourFloats",
            cat,
            cls._v1_inputs(),
            ("FLOAT_LIST",),
            ("float_list",),
        )

    @classmethod
    def _v1_inputs(s):
        return {
            "required": {
                "float_1": ("FLOAT", {"default": 1.0, "step": 0.01, "min": -10.0, "max":10.0}),
                "float_2": ("FLOAT", {"default": 1.0, "step": 0.01, "min": -10.0, "max":10.0}),
                "float_3": ("FLOAT", {"default": 1.0, "step": 0.01, "min": -10.0, "max":10.0}),
                "float_4": ("FLOAT", {"default": 1.0, "step": 0.01, "min": -10.0, "max":10.0}),
            },
        }
                
    
    @classmethod
    def execute(cls, float_1, float_2, float_3, float_4):
        float_list = [float_1, float_2, float_3, float_4,]
        return (float_list,)

class EightFloats(IO.ComfyNode):
    '''
    8 Floats
    '''
    @classmethod
    def define_schema(cls):
        return node(
            "EightFloats",
            cat,
            cls._v1_inputs(),
            ("FLOAT_LIST",),
            ("float_list",),
        )

    @classmethod
    def _v1_inputs(s):
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
                
    
    @classmethod
    def execute(cls, float_1, float_2, float_3, float_4, float_5, float_6, float_7, float_8):
        float_list = [float_1, float_2, float_3, float_4, float_5, float_6, float_7, float_8]
        return (float_list,)

class FloatListInterpreter1(IO.ComfyNode):  
    '''   
    Decode `Float` value(s) from `Float list`.
    
    Inputs:
    float_list      - Float list
    Start_At_Index  - If `Start_At_Index` is greater than length of `Float list`, it will restart from `0`
    
    Outputs:
    float(0~N)      - Float list    
    '''
    @classmethod
    def define_schema(cls):
        return node(
            "FloatListInterpreter1",
            cat,
            cls._v1_inputs(),
            ("FLOAT", ),
            ("float", ),
        )

    
    @classmethod
    def _v1_inputs(s):
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
        
    
    @classmethod
    def execute(cls, float_list, Start_At_Index):
        new_list = FloatListInterpreter(float_list, Start_At_Index)
            
        return (new_list[0],)
class FloatListInterpreter4(IO.ComfyNode):  
    '''   
    Same as FloatListInterpreter1
    '''
    @classmethod
    def define_schema(cls):
        return node(
            "FloatListInterpreter4",
            cat,
            cls._v1_inputs(),
            ("FLOAT", "FLOAT", "FLOAT", "FLOAT",),
            ("float_1", "float_2", "float_3", "float_4", ),
        )

    
    @classmethod
    def _v1_inputs(s):
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
        
    
    @classmethod
    def execute(cls, float_list, Start_At_Index):
        new_list = FloatListInterpreter(float_list, Start_At_Index, 4)
            
        return (new_list[0],new_list[1],new_list[2],new_list[3],)
    
class FloatListInterpreter8(IO.ComfyNode):  
    '''   
    Same as FloatListInterpreter1
    '''
    @classmethod
    def define_schema(cls):
        return node(
            "FloatListInterpreter8",
            cat,
            cls._v1_inputs(),
            ("FLOAT", "FLOAT", "FLOAT", "FLOAT","FLOAT", "FLOAT", "FLOAT", "FLOAT",),
            ("float_1", "float_2", "float_3", "float_4", "float_5", "float_6", "float_7", "float_8",),
        )

    
    @classmethod
    def _v1_inputs(s):
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
        
    
    @classmethod
    def execute(cls, float_list, Start_At_Index):
        new_list = FloatListInterpreter(float_list, Start_At_Index, 8)
            
        return (new_list[0],new_list[1],new_list[2],new_list[3],new_list[4],new_list[5],new_list[6],new_list[7],)
    
class StepsAndCfg(IO.ComfyNode):
    '''
    Steps and CFG
    '''
    @classmethod
    def define_schema(cls):
        return node(
            "StepsAndCfg",
            cat,
            cls._v1_inputs(),
            ("INT", "FLOAT",),
            ("STEPS", "CFG",),
        )

    @classmethod
    def _v1_inputs(s):
        return {
            "required": {
                "steps": ("INT", {"default": 30, "step": 1, "min": 1}),
                "cfg": ("FLOAT", {"default": 7.0, "step": 0.01, "min": 0.0}),
            },
        }
                
    
    @classmethod
    def execute(cls, steps, cfg):
        return (steps, cfg,)
    

