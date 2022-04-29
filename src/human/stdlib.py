from .interpret import (
    __functions__, __objects__, 
    Function, DefinitionPattern, 
    Argument, 
    ParserException, 
    get_best_match, 
    UNDEFINED, 
    add_or_set_variable, 
    interpret_file, interpret_string, 
    Variable, 
    Log
)
from word2number import w2n
from num2words import num2words
from thelittlethings import Mutable

def auto_interpret(arg: "Argument"):
    try:
        return interpret_file(arg.value)
    except FileNotFoundError:
        return interpret_string(arg.value)

def number(arg: Argument):
    try:
        return float(arg.value)
    except ValueError:
        try:
            return w2n.word_to_num(arg.value)
        except ValueError as e:
            raise ParserException(f"'{arg.value}' could not be resolved to a number.", 0) from e


def add(a, b):
    return number(a) + number(b)


def sub(a, b):
    return number(a) - number(b)


def rsub(a, b):
    return number(b) - number(a)


def mul(a, b):
    return number(a) * number(b)


def div(a, b):
    return number(a) / number(b)


def rdiv(a, b):
    return number(b) / number(a)


def remainder(a, b):
    return number(a) % number(b)


def add_to(value: Argument, var: Argument):
    if (func := get_best_match(var.name)) is not UNDEFINED:
        if isinstance(func, Variable):
            var.value = number(var) + number(value)
            __objects__[func.index] = var.value
            return var.value
    
    raise ParserException(f"'{var.name}' is not a variable.", 0)

def sub_from(value: Argument, var: Argument):
    if (func := get_best_match(var.name)) is not UNDEFINED:
        if isinstance(func, Variable):
            var.value = number(var) - number(value)
            __objects__[func.index] = var.value
            return var.value

    raise ParserException(f"'{var.name}' is not a variable.", 0)

def mul_by(var: Argument, value: Argument):
    if (func := get_best_match(var.name)) is not UNDEFINED:
        if isinstance(func, Variable):
            var.value = number(var) * number(value)
            __objects__[func.index] = var.value
            return var.value
    
    raise ParserException(f"'{var.name}' is not a variable.", 0)

def div_by(var: Argument, value: Argument):
    if (func := get_best_match(var.name)) is not UNDEFINED:
        if isinstance(func, Variable):
            var.value = number(var) / number(value)
            __objects__[func.index] = var.value
            return var.value

    raise ParserException(f"'{var.name}' is not a variable.", 0)

number_printing_mode = Mutable(0)

def print_out(arg: Argument):
    value = arg.value

    try:
        value = float(value)
    except ValueError:
        pass

    if number_printing_mode == 0:
        if isinstance(value, (float, int)):
            value = num2words(value)
    else:
        if isinstance(value, str):
            # custom check whether w2n ignores parts 
            # (it would output 2 for "filler two")
            if num2words(w2n.word_to_num(value)) == value:
                value = w2n.word_to_num(value)
        if number_printing_mode == 1:
            pass
        elif number_printing_mode == 2:
            if isinstance(value, str):
                value = w2n.word_to_num(value)
            if isinstance(value, (float, int)):
                value = f"{value:.2e}"


    Log(value, print_=True, file_path=None)
    return arg.value

def set_number_printing_mode(mode: Argument):
    if mode.value in ["words", "spelled out", "natural", "long"]:
        number_printing_mode.value = 0
    elif mode.value in ["decimal", "decimal notation", "float", "digits"]:
        number_printing_mode.value = 1
    elif mode.value in ["scientific notation", "scientific"]:
        number_printing_mode.value = 2
    
    return number_printing_mode.value

def get_value(var: Argument):
    return var.value


__functions__.extend(
    [        
        Variable("result", 0),

        Function(DefinitionPattern("print some value"), print_out),
        Function(DefinitionPattern("print out some value"), print_out),
        Function(DefinitionPattern("print some value to the console"), print_out),
        Function(DefinitionPattern("print out some value to the console"), print_out),

        Function(DefinitionPattern("set the number printing mode to some value"), set_number_printing_mode),

        Function(DefinitionPattern("some a + some b"), add),
        Function(DefinitionPattern("some a - some b"), sub),
        Function(DefinitionPattern("some a * some b"), mul),
        Function(DefinitionPattern("some a / some b"), div),
        Function(DefinitionPattern("some a % some b"), rdiv),
        Function(DefinitionPattern("some a plus some b"), add),
        Function(DefinitionPattern("some a minus some b"), sub),
        Function(DefinitionPattern("some a times some b"), mul),
        Function(DefinitionPattern("some a divided by some b"), div),
        Function(DefinitionPattern("add up some a and some b"), add),
        Function(DefinitionPattern("subtract some b from some a"), rsub),
        Function(DefinitionPattern("multiply some a by some b"), mul),
        Function(DefinitionPattern("divide some a by some b"), div),
        Function(DefinitionPattern("sum of some a and some b"), add),
        Function(DefinitionPattern("difference of some a and some b"), sub),
        Function(DefinitionPattern("product of some a and some b"), mul),
        Function(DefinitionPattern("quotient of some a and some b"), div),
        Function(DefinitionPattern("remainder of some a divided by some b"), remainder),
        Function(DefinitionPattern("add some a to some b"), add_to),
        Function(DefinitionPattern("add some a"), lambda value: add_to(value, Argument("result", __objects__[0]))),
        Function(DefinitionPattern("subtract some b from some a"), sub_from),
        Function(DefinitionPattern("subtract some b"), lambda value: sub_from(value, Argument("result", __objects__[0]))),
        Function(DefinitionPattern("multiply some a by some b"), mul_by),
        Function(DefinitionPattern("multiply by some a"), lambda value: mul_by(Argument("result", __objects__[0]), value)),
        Function(DefinitionPattern("divide some a by some b"), div_by),
        Function(DefinitionPattern("divide by some a"), lambda value: div_by(Argument("result", __objects__[0]), value)),
        
        Function(DefinitionPattern("some a > some b"), lambda a, b: number(a) > number(b)),
        Function(DefinitionPattern("some a < some b"), lambda a, b: number(a) < number(b)),
        Function(DefinitionPattern("some a >= some b"), lambda a, b: number(a) >= number(b)),
        Function(DefinitionPattern("some a <= some b"), lambda a, b: number(a) <= number(b)),
        Function(DefinitionPattern("some a == some b"), lambda a, b: number(a) == number(b)),
        Function(DefinitionPattern("some a != some b"), lambda a, b: number(a) != number(b)),
        Function(DefinitionPattern("some a is greater than some b"), lambda a, b: number(a) > number(b)),
        Function(DefinitionPattern("some a is less than some b"), lambda a, b: number(a) < number(b)),
        Function(DefinitionPattern("some a is greater than or equal to some b"), lambda a, b: number(a) >= number(b)),
        Function(DefinitionPattern("some a is less than or equal to some b"), lambda a, b: number(a) <= number(b)),
        Function(DefinitionPattern("some a is equal to some b"), lambda a, b: number(a) == number(b)),
        Function(DefinitionPattern("some a is not equal to some b"), lambda a, b: number(a) != number(b)),
        Function(DefinitionPattern("some a greater than some b"), lambda a, b: number(a) > number(b)),
        Function(DefinitionPattern("some a less than some b"), lambda a, b: number(a) < number(b)),
        Function(DefinitionPattern("some a greater than or equal to some b"), lambda a, b: number(a) >= number(b)),
        Function(DefinitionPattern("some a less than or equal to some b"), lambda a, b: number(a) <= number(b)),
        Function(DefinitionPattern("some a greater some b"), lambda a, b: number(a) > number(b)),
        Function(DefinitionPattern("some a less than some b"), lambda a, b: number(a) < number(b)),
        Function(DefinitionPattern("some a greater than or equal to some b"), lambda a, b: number(a) >= number(b)),
        Function(DefinitionPattern("some a less than or equal to some b"), lambda a, b: number(a) <= number(b)),

        Function(DefinitionPattern("some name is some value"), add_or_set_variable),
        Function(DefinitionPattern("set some name to some value"), add_or_set_variable),

        Function(DefinitionPattern("the some value"), get_value),
        Function(DefinitionPattern("get some value"), get_value),

        Function(DefinitionPattern("interpret some string"), auto_interpret),

        Function(DefinitionPattern("run some file"), auto_interpret),
    ]
)
