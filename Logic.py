cat = "Mira/Logic"

class SingleBooleanTrigger:
    '''
    A Boolean Trigger
    
    Inputs:
    bool    - Boolean trigger
    
    Outputs:
    bool    - Boolean value same as input
    '''
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "bool": ("BOOLEAN", {
                    "default": False,
                }),                
            },
        }
                
    RETURN_TYPES = ("BOOLEAN",)
    RETURN_NAMES = ("bool",)
    FUNCTION = "SingleBooleanTriggerEx"
    CATEGORY = cat
    
    def SingleBooleanTriggerEx(self, bool):
        return (bool,)
    
class TwoBooleanTrigger:
    '''
    2 Boolean Triggers
    
    Refer to SingleBooleanTrigger
    '''
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "bool_1": ("BOOLEAN", {"default": False,}),
                "bool_2": ("BOOLEAN", {"default": False,}),
            },
        }
                
    RETURN_TYPES = ("BOOLEAN","BOOLEAN",)
    RETURN_NAMES = ("bool_1","bool_2",)
    FUNCTION = "TwoBooleanTriggerEx"
    CATEGORY = cat
    
    def TwoBooleanTriggerEx(self, bool_1, bool_2,):
        return (bool_1, bool_2,)
    
class FourBooleanTrigger:
    '''
    4 Boolean Triggers
    
    Refer to SingleBooleanTrigger
    '''
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "bool_1": ("BOOLEAN", {"default": False,}),
                "bool_2": ("BOOLEAN", {"default": False,}),
                "bool_3": ("BOOLEAN", {"default": False,}),
                "bool_4": ("BOOLEAN", {"default": False,}),
            },
        }
                
    RETURN_TYPES = ("BOOLEAN","BOOLEAN","BOOLEAN","BOOLEAN",)
    RETURN_NAMES = ("bool_1","bool_2","bool_3","bool_4",)
    FUNCTION = "FourBooleanTriggerEx"
    CATEGORY = cat
    
    def FourBooleanTriggerEx(self, bool_1, bool_2, bool_3, bool_4):
        return (bool_1, bool_2, bool_3, bool_4,)

class SixBooleanTrigger:
    '''
    6 Boolean Triggers
    
    OH... come on, It's all the same. Wanna know where I need those triggers? A LoRA train.
    Refer to SingleBooleanTrigger
    '''
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "bool_1": ("BOOLEAN", {"default": False,}),
                "bool_2": ("BOOLEAN", {"default": False,}),
                "bool_3": ("BOOLEAN", {"default": False,}),
                "bool_4": ("BOOLEAN", {"default": False,}),
                "bool_5": ("BOOLEAN", {"default": False,}),
                "bool_6": ("BOOLEAN", {"default": False,}),
            },
        }
                
    RETURN_TYPES = ("BOOLEAN","BOOLEAN","BOOLEAN","BOOLEAN","BOOLEAN","BOOLEAN",)
    RETURN_NAMES = ("bool_1","bool_2","bool_3","bool_4","bool_5","bool_6",)
    FUNCTION = "SixBooleanTriggerEx"
    CATEGORY = cat
    
    def SixBooleanTriggerEx(self, bool_1, bool_2, bool_3, bool_4, bool_5, bool_6):
        return (bool_1, bool_2, bool_3, bool_4, bool_5, bool_6,)
    
    