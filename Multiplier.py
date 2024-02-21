cat = "Mira/Multiplier"

class IntMultiplier:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "input_value": ("INT", {
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
    RETURN_NAMES = ("Result (INT)","Result (STRING)",)
    FUNCTION = "execute"
    CATEGORY = cat

    def execute(self, input_value, multiply_value):
        result = input_value * multiply_value
        return (result, str(result),)
    
class FloatMultiplier:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "input_value": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,           
                    "step": 0.1,
                    "display": "number" 
                }),
                "multiply_value": ("FLOAT", {
                    "default": 1.5,
                    "min": 0,           
                    "step": 0.1,
                    "display": "number" 
                })
            },
        }

    RETURN_TYPES = ("FLOAT","INT", "STRING",)
    RETURN_NAMES = ("Result (FLOAT)", "Result (INT)","Result (STRING)",)
    FUNCTION = "execute"
    CATEGORY = cat

    def execute(self, input_value, multiply_value):
        result = input_value * multiply_value
        return (result, int(result), str(result),)
    
