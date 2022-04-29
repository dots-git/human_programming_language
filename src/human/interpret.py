from typing import Callable, Dict, List, Tuple
from .parse import __functions__, __objects__, Function, DefinitionPattern
from thelittlethings import Log, UNDEFINED, EList
from .utils import clean_single_outer_parenths


def get_object(index: "Argument"):
    return __objects__[index.value]


def set_object(index, value):
    __objects__[index] = value


class Variable(Function):
    def __init__(self, name, index):
        super().__init__(DefinitionPattern(name), get_object, (index,))
        self.name = name
        self.index = index


def add_or_set_variable(name: "Argument", value: "Argument"):
    if name.name == "":
        name = name.value
    else:
        name = name.name

    existing = UNDEFINED
    existing = get_best_match(name)

    if isinstance(existing, Variable):
        __objects__[existing.index] = value.value
        return value.value
    else:
        if isinstance(existing, Function):
            __functions__.remove(existing)

        __objects__.append(value.value)
        __functions__.append(Variable(name, len(__objects__) - 1))

        __functions__.sort(
            key=lambda x: sum(
                len(val.value) for val in x.pattern.pattern if val.type == "match"
            ),
            reverse=True,
        )
        
        return value.value


class FunctionCall:
    def __init__(self, function: Function, args: Tuple, kwargs: Dict):

        self.function = function

        args = list(args)

        for i, arg in enumerate(args):
            if isinstance(arg, str):
                args[i] = Argument(arg, live_eval=True)
            elif isinstance(arg, Argument):
                args[i] = arg
                arg.live_eval = True
            else:
                args[i] = Argument("", arg)

        for key, kwarg in kwargs.items():
            if isinstance(kwarg, str):
                kwargs[key] = Argument(kwarg, live_eval=True)
            elif isinstance(kwarg, Argument):
                kwargs[key] = kwarg
                kwarg.live_eval = True
            else:
                kwargs[key] = Argument("", kwarg)


        self.args: List[Argument] = args
        self.kwargs: Dict[str, Argument] = kwargs

    def __call__(self):

        evaluated_args = []

        for arg in self.args:
            evaluated_args.append(arg.evaluated())

        evaluated_kwargs = {}
        for key, value in self.kwargs.items():
            evaluated_kwargs[key] = value.evaluated()

        rv = self.function.function(*evaluated_args, **evaluated_kwargs)

        __objects__[0] = rv

        return rv

    @staticmethod
    def from_function(func: Function, string):
        return FunctionCall(
            func,
            (*func.pattern.match_vars_in(string).values(), *func.additional_args),
            func.additional_kwargs,
        )


class Argument:
    def __init__(self, name: str, value=UNDEFINED, live_eval=False) -> None:

        self.live_eval = live_eval
        self.value = value

        had_parenths = True
        while had_parenths:
            self.name = name.strip()
            
            if (
                self.name.startswith("'")
                and self.name.endswith("'")
                or self.name.startswith('"')
                and self.name.endswith('"')
            ):
                self.value = self.name[1:-1]
                self.live_eval = False
                break

            self.name, had_parenths = clean_single_outer_parenths(self.name)

        if self.value is UNDEFINED:

            if (func := get_best_match(self.name)) is not UNDEFINED:
                self.value = FunctionCall.from_function(func, self.name)

            if self.value is UNDEFINED:
                self.value = self.name
            else:
                live_eval = False

    def evaluated(self):
        if self.live_eval and isinstance(self.value, str):
            if (func := get_best_match(self.name)) is not UNDEFINED:
                self.value = FunctionCall.from_function(func, self.name)

        if isinstance(self.value, FunctionCall):
            evaluated_arg = Argument(self.name, self.value())
            return evaluated_arg

        return self

    def __repr__(self) -> str:
        return f"Argument({self.name}, {self.value})"


class Keyword:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"Keyword({self.name}, {self.value})"


from src.human.parse import ParserException, HumanSyntaxError, get_best_match


__functions__.sort(
    key=lambda x: sum(
        len(val.value) for val in x.pattern.pattern if val.type == "match"
    ),
    reverse=True,
)


def interpret_line(string: str, file_name=None, full_file=None, start_index=None):

    if (func := get_best_match(string)) is not UNDEFINED:
        return FunctionCall.from_function(func, string)()

    if file_name is None:
        file_name = "string"
    if full_file is None:
        full_file = string
    if start_index is None:
        start_index = 0
    raise HumanSyntaxError(
        "No matching function found", file_name, full_file, start_index + 0, 0
    )


def interpret_string(string: str):
    funcs = compile_string(string)
    
    for func in funcs:
        func()
    
    return __objects__[0]


def interpret_file(file_name: str):
    with open(file_name) as f:
        return interpret_string(f.read())


def compile_line(string: str, file_name=None, full_file=None, start_line=None):

    if (func := get_best_match(string)) is not UNDEFINED:
        return FunctionCall.from_function(func, string)

    if file_name is None:
        file_name = "string"
    if full_file is None:
        full_file = string
    if start_line is None:
        start_line = 0
    raise HumanSyntaxError(
        f"No matching function or variable found for '{string}'", file_name, string, start_line, 0
    )


class IfStatement(FunctionCall):
    def __init__(self, condition: FunctionCall, true_branch: Callable, false_branch: "Callable | None" = None):
        self.condition = condition
        self.true_branch = true_branch
        self.false_branch = false_branch

    def __call__(self):
        if self.condition():
            self.true_branch()
        elif self.false_branch:
            self.false_branch()


def compile_string(string: str, file_name=None, full_file=None, start_line=None):

    if file_name is None:
        file_name = "string"
    if full_file is None:
        full_file = string
    if start_line is None:
        start_line = 0

    lines: List[str] = string.splitlines()


    indentation = 0
    for line in lines:
        while line[:indentation + 1] == " " * (indentation + 1):
            indentation += 1
        
        if not all(char == 0 for char in line):
            break


    for i, line in enumerate(lines):
        if line[:indentation] != " " * indentation:
            for char in line:
                if char != " ":
                    raise HumanSyntaxError(
                        f"Indentation error (expected {indentation} spaces)",
                        file_name,
                        line,
                        start_line + i,
                        line.index(char),
                    )
        
        lines[i] = line[indentation:]
    
    
    lines =  [line for line in lines if not line.startswith("#")]

    compiled_lines = []

    function_def_lines: Dict[int, Function] = {}

    for i, line in enumerate(lines):
        
        if "means:" in line:
            split_line = lines[i].split("means:")
            if len(split_line) > 2:
                raise HumanSyntaxError(
                    "Invalid function definition",
                    file_name,
                    full_file,
                    start_line + i,
                )
            definition_pattern = DefinitionPattern(split_line[0])

            lines[i] = ""

            func = Function(
                definition_pattern,
                None
            )

            __functions__.append(func)

            __functions__.sort(
                key=lambda x: sum(
                    len(val.value) for val in x.pattern.pattern if val.type == "match"
                ),
                reverse=True,
            )

            function_def_lines[i] = func


    for i, line in enumerate(lines):

        # check for comments
        if lines[i].startswith("#"):
            lines[i] = lines[i] = ""

        # check for a function definition
        if i in function_def_lines:

            # find the indented block
            code_block = EList()
            j = i + 1
            if not (lines[j].startswith(" ") or lines[j] == ""):
                raise HumanSyntaxError(
                    "Expected indented block for function definition",
                    file_name,
                    full_file,
                    start_line + i,
                    0,
                )
            while j < len(lines) and (lines[j].startswith(" ") or lines[j] == ""):
                code_block.append(lines[j])
                lines[j] = ""
                j += 1
            # compile to function
            try:       
                   
                function_def_lines[i].function = compile_to_function(
                        "\n".join(code_block),
                        f"function '{split_line[0]}' in {file_name}",
                        full_file,
                        start_line + i,
                        [
                            var.value
                            for var in function_def_lines[i].pattern.pattern
                            if var.type == "var"
                        ],
                    )
                

            except ParserException as e:
                raise HumanSyntaxError(
                    str(e), file_name, full_file, start_line + i, e.index
                ) from e
            
            function_def_lines.pop(i)

        elif lines[i].lower().startswith("if") and lines[i].lower().endswith(":"):
            lines[i] = lines[i][2:-1]
            lines[i] = lines[i].strip()
            if lines[i].lower().endswith("then"):
                lines[i] = lines[i][:-4].strip()

                if lines[i].lower().endswith(","):
                    lines[i] = lines[i][:-1].strip()
            
            # compile the condition
            condition = compile_line(lines[i], file_name, full_file, start_line + i)
            lines[i] = ""

            # find the indented block
            code_block = EList()
            j = i + 1
            if not (lines[j].startswith(" ") or lines[j] == ""):
                raise HumanSyntaxError(
                    "Expected indented block for if statement",
                    file_name,
                    full_file,
                    start_line + i,
                    0,
                )
            while j < len(lines) and (lines[j].startswith(" ") or lines[j] == ""):
                code_block.append(lines[j])
                lines[j] = ""
                j += 1
            # compile to function
            try:
                true_branch = compile_to_function(
                    "\n".join(code_block),
                    f"true branch of if statement in {file_name}",
                    full_file,
                    start_line + i,
                    []
                )
            except ParserException as e:
                raise HumanSyntaxError(
                    str(e), file_name, full_file, start_line + i, e.index
                ) from e
            
            false_branch = None

            # check for else
            if j < len(lines) and lines[j].lower().strip() == "else:":
                # hide the else statement
                lines[j] = ""

                j += 1
                code_block = EList()
                if not (lines[j].startswith(" ") or lines[j] == ""):
                    raise HumanSyntaxError(
                        "Expected indented block for else statement",
                        file_name,
                        full_file,
                        start_line + i,
                        0,
                    )

                while j < len(lines) and (lines[j].startswith(" ") or lines[j] == ""):
                    code_block.append(lines[j])
                    lines[j] = ""
                    j += 1
                # compile the function
                try:
                    false_branch = compile_to_function(
                        "\n".join(code_block),
                        f"false branch of if statement in {file_name}",
                        full_file,
                        start_line + i,
                        []
                    )

                except ParserException as e:
                    raise HumanSyntaxError(
                        str(e), file_name, full_file, start_line + i, e.index
                    ) from e

            compiled_lines.append(IfStatement(condition, true_branch, false_branch))
        
        elif lines[i] != "":
            # compile the line
            compiled_lines.append(
                compile_line(lines[i], file_name, full_file, start_line + i)
            )

    return compiled_lines


def compile_to_function(
    string: str, file_name=None, full_file=None, start_line=None, vars=[]
) -> Callable:

    if file_name is None:
        file_name = "string"
    if full_file is None:
        full_file = string
    if start_line is None:
        start_line = 0

    compiled_code = compile_string(string, file_name, full_file, start_line)

    def run(*args: Argument):
        for var, arg in zip(vars, args):
            add_or_set_variable(Argument(var, var), arg)

        for func in compiled_code:
            func()

        return __objects__[0]

    return run


def compile_file(file_name: str):
    with open(file_name) as f:
        return compile_string(f.read())


def compile_file_to_function(file_name: str):
    with open(file_name) as f:
        return compile_to_function(f.read(), file_name)

