from PIL import Image
import math
from .Mask import LoadImagePNG
from .Util import AlwaysEqualProxy

cat = "Mira/Logic"
cat74 = "Mira/Logic/74"

def CheckXOR(A = None, B = None):
    if None is A and None is B:
        return None            
    elif None is not A and None is B:
        return A            
    elif None is A and None is not B:
        return B           
    #elif None is not A and None is not B:
    return None

def CheckEvenOrOdd(num):       
    if num & 1:
        return (True, 'True',)
    else:
        return (False, 'False',)

def BooleanListInterpreter(bool_list, Start_At_Index, NOT_Mode = False, times = 1):
    new_list = []
    index = Start_At_Index
    list_len = len(bool_list)
    
    for _ in range(times):
        # not recommend, but this would be fun
        while index >= list_len:
            index = index - list_len
        
        if NOT_Mode is True:
            new_bool = not bool_list[index]
        else:
            new_bool = bool_list[index]
            
        new_list.append(new_bool)      
        index = index + 1
        
    return (new_list)              

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
    
    Inputs:
    bool        - Boolean trigger
    
    Outputs:
    bool_list   - Boolean list for `BooleanListInterpreter`
    '''
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "bool_1": ("BOOLEAN", {"default": False,}),
                "bool_2": ("BOOLEAN", {"default": False,}),
            },
        }
                
    RETURN_TYPES = ("BOOLEAN_LIST",)
    RETURN_NAMES = ("bool_list",)
    FUNCTION = "TwoBooleanTriggerEx"
    CATEGORY = cat
    
    def TwoBooleanTriggerEx(self, bool_1, bool_2,):
        bool_list = [bool_1, bool_2]
        return (bool_list,)
    
class FourBooleanTrigger:
    '''
    4 Boolean Triggers
    
    Refer to TwoBooleanTrigger
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
                
    RETURN_TYPES = ("BOOLEAN_LIST",)
    RETURN_NAMES = ("bool_list",)
    FUNCTION = "FourBooleanTriggerEx"
    CATEGORY = cat
    
    def FourBooleanTriggerEx(self, bool_1, bool_2, bool_3, bool_4):
        bool_list = [bool_1, bool_2, bool_3, bool_4]
        return (bool_list,)

class SixBooleanTrigger:
    '''
    6 Boolean Triggers
    
    OH... come on, It's all the same. Wanna know where I need those triggers? A LoRA train.
    Refer to TwoBooleanTrigger
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
                
    RETURN_TYPES = ("BOOLEAN_LIST",)
    RETURN_NAMES = ("bool_list",)
    FUNCTION = "SixBooleanTriggerEx"
    CATEGORY = cat
    
    def SixBooleanTriggerEx(self, bool_1, bool_2, bool_3, bool_4, bool_5, bool_6):
        bool_list = [bool_1, bool_2, bool_3, bool_4, bool_5, bool_6]
        return (bool_list,)
    
class EightBooleanTrigger:
    '''
    8 Boolean Triggers
    
    Refer to TwoBooleanTrigger
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
                "bool_7": ("BOOLEAN", {"default": False,}),
                "bool_8": ("BOOLEAN", {"default": False,}),
            },
        }
                
    RETURN_TYPES = ("BOOLEAN_LIST",)
    RETURN_NAMES = ("bool_list",)                
    FUNCTION = "EightBooleanTriggerEx"
    CATEGORY = cat
    
    def EightBooleanTriggerEx(self, bool_1, bool_2, bool_3, bool_4, bool_5, bool_6, bool_7, bool_8):
        bool_list = [bool_1, bool_2, bool_3, bool_4, bool_5, bool_6, bool_7, bool_8]
        return (bool_list,)    
    
class LogicNot:
    '''   
    Always return Boolean Not
    
    Input | Output
    True    False
    False   True    
    '''
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "bool": ("BOOLEAN", {"default": True,}),
            },
        }
                
    RETURN_TYPES = ("BOOLEAN","STRING")
    RETURN_NAMES = ("not_bool", "result")
    FUNCTION = "LogicNotEx"
    CATEGORY = cat
    
    def LogicNotEx(self, bool,):
        return (not bool, str(not bool),)
    
class EvenOrOdd:
    '''   
    Check if a `Integer` is odd or even.   
    
    Input | Output
    Odd     True    
    Even    False
    '''
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "num": ("INT", {"default": 1,}),
            },
        }
                
    RETURN_TYPES = ("BOOLEAN", "STRING")
    RETURN_NAMES = ("bool_Odd_True", "result")
    FUNCTION = "EvenOrOddEx"
    CATEGORY = cat
    
    def EvenOrOddEx(self, num,):       
        return CheckEvenOrOdd(num)
    
class EvenOrOddList:
    '''   
    Checks whether each `digit` (decimal) of the input `integer` is odd or even, 
    and returns `true` for even numbers and `false` for odd numbers. 
    The final output is a `Boolean List` which is connected to the `Boolean List Interpreter`. 
    If the input `Number of digits` is less than the `Requirement`, 
    it will go back to the lowest digit to re-recognize and complete the list, 
    and the way the list is completed can be chosen as `as is` or `not`. 
    The output node `String` displays the actual results.

    Inputs:
    integer     - Recommend connect to `Seed Generator`
    quantity    - Length of the `Boolean list`, (I think) 16 for now is enough...
    NOT_filling - Filling Algorithm, `Enable` for switch `NOT` and "AS IS" in future loop, `Disable` for `AS IS` in every loop
    
    Outputs:
    bool_list   - Boolean list
    result      - String result
    
    Odd     True    
    Even    False
    '''
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "integer": ("INT", {
                    "default": 1234567890, 
                    "min": 0, 
                    "max": 0xffffffffffffffff,
                    "display": "input"
                }),
                "quantity": ("INT", {
                    "default": 1, 
                    "min": 1, 
                    "max": 16
                }),
                "NOT_filling": ("BOOLEAN", {
                    "default": False, 
                }),
            },            
        }
        
    RETURN_TYPES = ("BOOLEAN_LIST", "STRING")
    RETURN_NAMES = ("bool_list_Odd_True", "result")
    FUNCTION = "EvenOrOddListEx"
    CATEGORY = cat
    
    def EvenOrOddListEx(self, integer, quantity, NOT_filling):        
        bool_list = []
        string_list = 'Input = ' + str(integer) + ' Times = ' + str(len(str(integer))) + '\nResults\n'
        new_seed = integer       
        swap = False
        
        for _ in range(quantity):
            new_bool = CheckEvenOrOdd(new_seed)
            if False is swap:
                bool_list.append(new_bool[0])
                string_list = string_list + str(new_bool[0]) + '(' + str(new_seed) + ')\n'
            else:
                bool_list.append(not new_bool[0])
                string_list = string_list + str(not new_bool[0]) + '(' + str(new_seed) + ')\n'
                
            new_seed = math.floor(new_seed * 0.1)            
            if 0 >= new_seed:
                new_seed = integer
                if True is NOT_filling and swap is not True:
                    swap = True
                else:
                    swap = False   
                         
        return(bool_list, string_list, )
    
class BooleanListInterpreter1:  
    '''   
    Decode `Boolean` value(s) from `Boolean list`.
    
    Inputs:
    bool_list       - Boolean list
    Start_At_Index  - If `Start_At_Index` is greater than length of `Boolean list`, it will restart from `0`
    NOT_Mode       - Inverts the Boolean value from input to output (1->0 0->1)
    
    Outputs:
    bool(0~N)   - Boolean list    
    '''
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "bool_list": ("BOOLEAN_LIST", {
                    "display": "input", 
                }),
                "Start_At_Index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "step": 1,
                    "display": "number" 
                }),            
                "NOT_Mode": ("BOOLEAN", {
                    "default": False, 
                }),    
            },            
        }
        
    RETURN_TYPES = ("BOOLEAN", )
    RETURN_NAMES = ("bool", )
    FUNCTION = "BooleanListInterpreter1Ex"
    CATEGORY = cat
    
    def BooleanListInterpreter1Ex(self, bool_list, Start_At_Index, NOT_Mode):
        new_list = BooleanListInterpreter(bool_list, Start_At_Index, NOT_Mode)
            
        return (new_list[0],)
    
class BooleanListInterpreter4:  
    '''   
    Same as BooleanListInterpreter1
    '''
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "bool_list": ("BOOLEAN_LIST", {
                    "display": "input", 
                }),
                "Start_At_Index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "step": 1,
                    "display": "number" 
                }),             
                "NOT_Mode": ("BOOLEAN", {
                    "default": False, 
                }),   
            },            
        }
        
    RETURN_TYPES = ("BOOLEAN", "BOOLEAN", "BOOLEAN", "BOOLEAN",)
    RETURN_NAMES = ("bool_0", "bool_1", "bool_2", "bool_3", )
    FUNCTION = "BooleanListInterpreter4Ex"
    CATEGORY = cat
    
    def BooleanListInterpreter4Ex(self, bool_list, Start_At_Index, NOT_Mode):
        new_list = BooleanListInterpreter(bool_list, Start_At_Index, NOT_Mode, 4)
            
        return (new_list[0],new_list[1],new_list[2],new_list[3],)
    
class BooleanListInterpreter8:  
    '''   
    Same as BooleanListInterpreter1
    '''
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "bool_list": ("BOOLEAN_LIST", {
                    "display": "input", 
                }),
                "Start_At_Index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "step": 1,
                    "display": "number" 
                }),                
                "NOT_Mode": ("BOOLEAN", {
                    "default": False, 
                }), 
            },            
        }
        
    RETURN_TYPES = ("BOOLEAN", "BOOLEAN", "BOOLEAN", "BOOLEAN","BOOLEAN", "BOOLEAN", "BOOLEAN", "BOOLEAN",)
    RETURN_NAMES = ("bool_0", "bool_1", "bool_2", "bool_3", "bool_4", "bool_5", "bool_6", "bool_7",)
    FUNCTION = "BooleanListInterpreter8Ex"
    CATEGORY = cat
    
    def BooleanListInterpreter8Ex(self, bool_list, Start_At_Index, NOT_Mode):
        new_list = BooleanListInterpreter(bool_list, Start_At_Index, NOT_Mode, 8)
            
        return (new_list[0],new_list[1],new_list[2],new_list[3],new_list[4],new_list[5],new_list[6],new_list[7],)
    
class FunctionSwap:
    """
    Swap `func1` and `func2` outputs depends on `trigger`.
    
    Now `func2` is `optional`, if `NOT connected` or `function bypassed`, both `Outputs` will return `func1`.    
    
    Inputs:
    swap    - True or False
    func1   - Any function. E.g. `Mask_1`.
    func2   - Any function. E.g. `Mask_2`.
    
    Outputs:
    | swap  |   A   |   B   |
    | True  | func2 | func1 |
    | False | func1 | func2 |
    """

    @classmethod
    def INPUT_TYPES(s):
        return {
            "optional": {
                "func2": (AlwaysEqualProxy("*"),),
            },
            "required": {
                "func1": (AlwaysEqualProxy("*"),),
                "trigger": ("BOOLEAN", {"default": False, "display":"input",}),
            },
        }

    RETURN_TYPES = (AlwaysEqualProxy("*"), AlwaysEqualProxy("*"),)
    RETURN_NAMES = ("A", "B", )
    FUNCTION = "FunctionSwapEx"
    CATEGORY = cat

    def FunctionSwapEx(self, trigger, func1, func2 = None):
        if func2 is None:
            return (func1, func1,)
        
        if True is trigger:
            return (func2, func1,)
        else:
            return (func1, func2,)    
        
class FunctionSelectAuto:
    """
    Function Select Auto
    
    Automatically select `func1` or `func2` outputs depends on which one is `NOT None`.
    `func1` has higher priority.
    
    Inputs:
    func1   - Any function. E.g. `Image from Model Image Upscaler `.
    func2   - Any function. E.g. `Image from Vae Decode`.
    
    Outputs:
    |   Y   |   func1   |   func2   |
    | None  |   None    |   None    |
    | func1 |   func1   |   None    |
    | func1 |   func1   |   func2   |
    | func2 |   None    |   func2   |
    """

    @classmethod
    def INPUT_TYPES(s):
        return {
            "optional": {
                "func1": (AlwaysEqualProxy("*"),),
                "func2": (AlwaysEqualProxy("*"),),
            },
        }

    RETURN_TYPES = (AlwaysEqualProxy("*"),)
    RETURN_NAMES = ("Y",  )
    FUNCTION = "FunctionSelectAutoEx"
    CATEGORY = cat

    def FunctionSelectAutoEx(self, func1 = None, func2 = None):
        if func1 is None and func2 is None:            
            return (None, )
        
        if func1 is not None:
            return (func1,)
        else:
            return (func2,)
    
class SN74LVC1G125:
    '''
    Single Bus Buffer Gate With Enable
    
    |  OE   |  A   |
    | True  |  Y   |
    | False | None |
    '''
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "OE": ("BOOLEAN", {"default": True, "display":"input",}),
                "A": (AlwaysEqualProxy("*"),),
            },
        }
        
    RETURN_TYPES = (AlwaysEqualProxy("*"), )
    RETURN_NAMES = ("Y",)
    FUNCTION = "SN74LVC1G125Ex"
    CATEGORY = cat74

    def SN74LVC1G125Ex(self, OE, A):
        if True is OE:
            return (A,)
        else:
            return (None,)    
        
class NoneToZero:
    '''   
    Check if the `check_none` is None, then set return value to `0`.
    '''
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "check_none": (AlwaysEqualProxy("*"),),
                "ret_img": ("IMAGE", {"display":"input"}),
                "ret_float": ("FLOAT", {"default": 1.0, "step": 0.0001}),
                "ret_int": ("INT", {"default": 1, "step": 1}),
            },
        }
        
    RETURN_TYPES = ("FLOAT", "INT", "IMAGE", AlwaysEqualProxy("*"),)
    RETURN_NAMES = ("ret_float", "ret_int", "ret_img", "none_image",)
    FUNCTION = "NoneToZeroEx"
    CATEGORY = cat

    def NoneToZeroEx(self, check_none, ret_float, ret_int, ret_img):
        if None is check_none:
            PngImage = Image.new("RGB", [2, 2])
            output_image = LoadImagePNG(PngImage)   
            return (0.0, 0, output_image, None, )
        else:
            return (ret_float, ret_int, ret_img, ret_img, )

# 74 Family               
class SN74HC1G86:
    '''
    Single 2-Input Exclusive-OR Gate
    
    |   A   |   B   |   Y  |
    | True  | True  | None |
    | False | False | None |
    | True  | False |  A   |
    | False | True  |  B   |
    '''
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "optional": {
                "A": (AlwaysEqualProxy("*"),),
                "B": (AlwaysEqualProxy("*"),),
            },
            "required": {
            },
        }
        
    RETURN_TYPES = (AlwaysEqualProxy("*"), )
    RETURN_NAMES = ("Y",)
    FUNCTION = "SN74HC86Ex"
    CATEGORY = cat74
    
    def SN74HC86Ex(self, A = None, B = None):
                
        Y = CheckXOR(A, B)
        return (Y,)
        
        
class SN74HC86:
    '''
    Quadruple 2-Input Exclusive-OR Gates
    
    |   A   |   B   |   Y  |
    | True  | True  | None |
    | False | False | None |
    | True  | False |  A   |
    | False | True  |  B   |
    '''
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "optional": {
                "A1": (AlwaysEqualProxy("*"),),
                "B1": (AlwaysEqualProxy("*"),),
                "A2": (AlwaysEqualProxy("*"),),
                "B2": (AlwaysEqualProxy("*"),),
                "A3": (AlwaysEqualProxy("*"),),
                "B3": (AlwaysEqualProxy("*"),),
                "A4": (AlwaysEqualProxy("*"),),
                "B4": (AlwaysEqualProxy("*"),),
            },
            "required": {
            },
        }
        
    RETURN_TYPES = (AlwaysEqualProxy("*"), AlwaysEqualProxy("*"), AlwaysEqualProxy("*"), AlwaysEqualProxy("*"), )
    RETURN_NAMES = ("1Y", "2Y", "3Y", "4Y",)
    FUNCTION = "SN74HC86Ex"
    CATEGORY = cat74
    
    def SN74HC86Ex(self, A1 = None, B1 = None, A2 = None, B2 = None, A3 = None, B3 = None, A4 = None, B4 = None):
                
        Y1 = CheckXOR(A1, B1)
        Y2 = CheckXOR(A2, B2)
        Y3 = CheckXOR(A3, B3)
        Y4 = CheckXOR(A4, B4)
        
        return (Y1, Y2, Y3, Y4,)
        
        