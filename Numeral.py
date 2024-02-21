cat = "Mira/Numeral"

class AlwaysEqualProxy(str):
#ComfyUI-Logic 
#refer: https://github.com/theUpsider/ComfyUI-Logic
    def __eq__(self, _):
        return True

    def __ne__(self, _):
        return False
    
class NumeralToString:
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
        
