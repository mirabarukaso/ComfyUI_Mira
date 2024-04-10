cat = "Mira/Arithmetic"

class IntMultiplication:
    '''   
    Inputs:
    input_value     - Integer number as A
    multiply_value  - Integer number as B
        
    Outputs:
    Result (INT)    - The result of A x B
    Result (STRING) - The result of A x B, and convert to string
    '''
    @classmethod
    def INPUT_TYPES(s):
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

    RETURN_TYPES = ("INT","STRING",)
    RETURN_NAMES = ("Result (INT)", "Result (STRING)",)
    FUNCTION = "IntMultiplicationEx"
    CATEGORY = cat

    def IntMultiplicationEx(self, int_value, multiply_value):
        result = int_value * multiply_value
        return (result, str(result),)
    
class IntToFloatMultiplication:
    '''   
    Inputs:
    int_value       - Integer number as A
    multiply_value  - Integer number as B
        
    Outputs:
    Result (INT)    - The result of A x B
    Result (STRING) - The result of A x B, and convert to string
    '''
    @classmethod
    def INPUT_TYPES(s):
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

    RETURN_TYPES = ("FLOAT","INT", "STRING",)
    RETURN_NAMES = ("Result (FLOAT)", "Result (INT)","Result (STRING)",)
    FUNCTION = "IntToFloatMultiplicationEx"
    CATEGORY = cat

    def IntToFloatMultiplicationEx(self, int_value, multiply_value):
        result = float(int_value) * multiply_value
        return (result, int(result), str(result),)
    
class FloatMultiplication:
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
    def INPUT_TYPES(s):
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

    RETURN_TYPES = ("FLOAT","INT", "STRING",)
    RETURN_NAMES = ("Result (FLOAT)", "Result (INT)","Result (STRING)",)
    FUNCTION = "ExFloatMultiplication"
    CATEGORY = cat

    def ExFloatMultiplication(self, float_value, multiply_value):
        result = float_value * multiply_value
        return (result, int(result), str(result),)
    
class IntSubtraction:
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
    def INPUT_TYPES(s):
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
        
    RETURN_TYPES = ("INT", "STRING", "INT",)
    RETURN_NAMES = ("Result (INT)", "Result (STRING)","subtracted_value",)
    FUNCTION = "ExIntSubtraction"
    CATEGORY = cat

    def ExIntSubtraction(self, int_value, subtracted_value):
        result = int_value - subtracted_value
        return (result, str(result), subtracted_value,)
    