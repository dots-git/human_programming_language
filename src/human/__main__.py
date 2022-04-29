from .interpret import compile_file_to_function
from thelittlethings import Log, to_string, EList
from .live_console import start_live_console
from . import stdlib

if __name__ == "__main__":
    import sys
    import pathlib

    # using EList to allow for deletion of elements 
    # while iterating without skipping elements
    sysargs = EList(sys.argv[1:])

    print_time = False

    for i, arg in sysargs.enumerate():
        if arg == "-t":
            print_time = True
            sysargs.pop(i)


    if len(sysargs) == 0:
        start_live_console()

    funcs = []

    for file in sysargs:
        funcs.append(compile_file_to_function(file))

    from time import perf_counter

    start = perf_counter()
    for func in funcs:
        func()
    end = perf_counter()

    if print_time:
        # get the full path of each file (consider relative paths)
        files = [pathlib.Path(file).resolve() for file in sysargs]
        Log(f"Execution of {to_string.list(files)} took {end - start} seconds")
