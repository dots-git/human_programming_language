from .interpret import Argument, add_or_set_variable, interpret_line, __functions__, __objects__, Function, DefinitionPattern, UNDEFINED

def start_live_console():
    __functions__.append(Function(DefinitionPattern("exit"), lambda: exit(0)))

    add_or_set_variable(
        Argument("traceback", "traceback"),
        Argument("", None)
    )

    while True:
        input_prompt = ""
        rv = __objects__[0]
        if rv is not UNDEFINED and rv is not None:
            input_prompt = f"{rv} "
        input_prompt += ">>> "
        line = input(input_prompt)
        try:
            interpret_line(line)
        except Exception as e:
            __objects__[0] = line

            import traceback
            