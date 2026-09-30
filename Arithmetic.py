from comfy_api.latest import IO
from .v3schema import node

cat = "Mira/Arithmetic"

class IntMultiplication(IO.ComfyNode):
    '''   
    Inputs:
    input_value     - Integer number as A
    multiply_value  - Integer number as B
        
    Outputs:
    Result (INT)    - The result of A x B
    Result (STRING) - The result of A x B, and convert to string
    '''
    @classmethod
    def define_schema(cls):
        return node(
            "IntMultiplication",
            cat,
            cls._v1_inputs(),
            ("INT","STRING",),
            ("Result (INT)", "Result (STRING)",),
        )

    @classmethod
    def _v1_inputs(s):
        return {
            "required": {
                "int_value": ("INT", {
                    "default": 0,
                    "min": 0,           # Minimum value
                    "display": "number" # Cosmetic only: display as "number" or "slider"
                }),
                "multiply_value": ("INT", {
                    "default": 2,
                    "min": 0,           # Minimum value
                    "display": "number" # Cosmetic only: display as "number" or "slider"
                })
            },
        }


    @classmethod
    def execute(cls, int_value, multiply_value):
        result = int_value * multiply_value
        return (result, str(result),)
    
class IntToFloatMultiplication(IO.ComfyNode):
    '''   
    Inputs:
    int_value       - Integer number as A
    multiply_value  - Integer number as B
        
    Outputs:
    Result (INT)    - The result of A x B
    Result (STRING) - The result of A x B, and convert to string
    '''
    @classmethod
    def define_schema(cls):
        return node(
            "IntToFloatMultiplication",
            cat,
            cls._v1_inputs(),
            ("FLOAT","INT", "STRING",),
            ("Result (FLOAT)", "Result (INT)","Result (STRING)",),
        )

    @classmethod
    def _v1_inputs(s):
        return {
            "required": {
                "int_value": ("INT", {
                    "default": 0,
                    "min": 0,           # Minimum value
                    "display": "number" # Cosmetic only: display as "number" or "slider"
                }),
                "multiply_value": ("FLOAT", {
                    "default": 1.5,
                    "min": 0,           
                    "step": 0.0000001,
                    "display": "number" 
                })
            },
        }


    @classmethod
    def execute(cls, int_value, multiply_value):
        result = float(int_value) * multiply_value
        return (result, int(result), str(result),)
    
class FloatMultiplication(IO.ComfyNode):
    '''   
    Inputs:
    float_value     - Float number as A
    multiply_value  - Float number as B
        
    Outputs:
    Result (FLOAT)  - The result of A x B
    Result (INT)    - The result of A x B, and trimmed to integer value
    Result (STRING) - The result of A x B, and convert to string
    '''
    @classmethod
    def define_schema(cls):
        return node(
            "FloatMultiplication",
            cat,
            cls._v1_inputs(),
            ("FLOAT","INT", "STRING",),
            ("Result (FLOAT)", "Result (INT)","Result (STRING)",),
        )

    @classmethod
    def _v1_inputs(s):
        return {
            "required": {
                "float_value": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,           
                    "step": 0.0000001,
                    "display": "number" 
                }),
                "multiply_value": ("FLOAT", {
                    "default": 1.5,
                    "min": 0,           
                    "step": 0.0000001,
                    "display": "number" 
                })
            },
        }


    @classmethod
    def execute(cls, float_value, multiply_value):
        result = float_value * multiply_value
        return (result, int(result), str(result),)
    
class IntSubtraction(IO.ComfyNode):
    '''   
    Inputs:
    int_value           - Integer number as A
    subtracted_value    - Integer number as B
        
    Outputs:
    Result (INT)        - The result of A - B
    Result (STRING)     - The result of A - B, and convert to string
    subtracted_value    - B as is
    '''
    @classmethod
    def define_schema(cls):
        return node(
            "IntSubtraction",
            cat,
            cls._v1_inputs(),
            ("INT", "STRING", "INT",),
            ("Result (INT)", "Result (STRING)","subtracted_value",),
        )

    
    @classmethod
    def _v1_inputs(s):
        return {
            "required": {
                "int_value": ("INT", {
                    "default": 0,
                    "min": 0,           
                    "display": "number" 
                }),
                "subtracted_value": ("INT", {
                    "default": 0,
                    "min": 0,           
                    "display": "number" 
                })
            },
        }
        

    @classmethod
    def execute(cls, int_value, subtracted_value):
        result = int_value - subtracted_value
        return (result, str(result), subtracted_value,)
    