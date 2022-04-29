from typing import Callable, Dict, List
from .utils import move_past_parenths
from thelittlethings import UNDEFINED


containment_chars = [
    ("(", ")"),
    ("[", "]"),
    ("{", "}"),
    ("'", "'"),
    ('"', '"'),
]




__objects__ = [UNDEFINED]    # all objects / values
__functions__: "List[Function]" = []  # all function / variable names



class ParserException(SyntaxError):
    def __init__(self, message, index):
        """
        :param message: The error message
        :param index: The index in the input string where the error occurred
        """
        self.message = message
        self.index = index

    def __str__(self) -> str:
        return f"{self.message}"


class HumanSyntaxError(SyntaxError):
    def __init__(self, message: str, file_name: str, string: str, start_line: int, index: int):
        """
        :param message: The error message
        :param file_name: The name of the file where the error occurred
        :param file_content: The content of the file where the error occurred
        :param index: The index in the input string where the error occurred
        """
        super().__init__(message)
        self.message = message
        self.file_name = file_name
        self.string = string
        self.start_line = start_line
        self.index = index

    def __str__(self):
        # determine the line and column for the index
        line_index = 0
        column_index = 0
        for i in range(self.index):
            if self.string[i] == "\n":
                line_index += 1
                column_index = 0
            else:
                column_index += 1

        return (
            f'\nIn file "{self.file_name}", in line {line_index + self.start_line + 1}:'
            f"\n\n{self.string.splitlines()[line_index]}\n"
            f"{' ' * (column_index)}{'^'}"
            f"\n{self.message}"
        )


class DefinitionPatternElement:
    def __init__(self, type: str, value: str):
        self.type = type
        self.value = value

    def __repr__(self) -> str:
        return f'{self.type} "{self.value}"'


class DefinitionPattern:
    def __init__(self, pattern_string):
        self.pattern: List[DefinitionPatternElement] = []

        i = 0
        while i < len(pattern_string):
            if pattern_string[i : i + 4] == "some":
                # find the following variable name
                i += 4
                while pattern_string[i] == " ":
                    i += 1

                exit_char = " "

                for char_pair in containment_chars:
                    if pattern_string[i] == char_pair[0]:
                        exit_char = char_pair[1]
                        break

                if exit_char != " ":
                    i += 1

                name = ""
                while i < len(pattern_string) and pattern_string[i] != exit_char:
                    name += pattern_string[i]
                    i += 1

                for char in name:
                    if (
                        not ord(char) in range(65, 91)
                        and not ord(char) in range(97, 123)
                        and not ord(char) in range(48, 57)
                        and not char in (" ", "_")
                    ):
                        raise ParserException(f"Invalid variable name: {name}", i)
                self.pattern.append(DefinitionPatternElement("var", name))

                if exit_char != " ":
                    i += 1

            else:
                if (
                    self.pattern
                    and self.pattern[-1].type == "match"
                    and not (
                        len(self.pattern[-1].value) > 0
                        and self.pattern[-1].value[-1] == " "
                    )
                ):
                    self.pattern[-1].value += pattern_string[i]
                elif pattern_string[i] != " ":
                    self.pattern.append(
                        DefinitionPatternElement("match", pattern_string[i])
                    )

                i += 1
        
        for i, element in enumerate(self.pattern):
            while element.value.endswith(" "):
                self.pattern[i].value = element.value[:-1]


    def get_match_length(self, string_to_match):
        """
        Returns a value for the length of the match of the pattern to the string.
        :param string_to_match: The string to match
        :return: The length of the longest match
        """
        match_length = 0

        string_index = 0
        pattern_index = 0

        if self.pattern[0].type == "match":
            if self.pattern[0].value != string_to_match[: len(self.pattern[0].value)]:
                raise ParserException(
                    f"Pattern {self.pattern} not found in {string_to_match}",
                    string_index,
                )

        while pattern_index < len(self.pattern):
            while self.pattern[pattern_index].type == "match":
                while (
                    string_to_match[
                        string_index : string_index
                        + len(self.pattern[pattern_index].value)
                    ]
                    != self.pattern[pattern_index].value
                ):
                    string_index += 1
                    if string_index + len(self.pattern[pattern_index].value) > len(
                        string_to_match
                    ):
                        raise ParserException(
                            f"Pattern {self.pattern} not found in {string_to_match}",
                            string_index,
                        )

                match_length += len(self.pattern[pattern_index].value)

                string_index += len(self.pattern[pattern_index].value)
                pattern_index += 1

                if pattern_index >= len(self.pattern):
                    break
            
            try:
                while string_to_match[string_index] == " ":
                    string_index += 1
            except IndexError:
                break

            if string_to_match[string_index] in (
                char_pair[0] for char_pair in containment_chars
            ):
                string_index = move_past_parenths(string_to_match, string_index)
            
            while string_index < len(string_to_match) and string_to_match[string_index] != " ":
                string_index += 1

            pattern_index += 1

    
        try:
            while string_to_match[string_index] == " ":
                string_index += 1
        except IndexError:
            return match_length

        raise ParserException(
            f"Pattern {self.pattern} not found in {string_to_match} (unexpected character {string_to_match[string_index]})",
            string_index,
        )



    def match_vars_in(self, string_to_match: str) -> Dict[str, str]:
        """
        Returns a dictionary of the variables in the pattern and their values.
        :param string_to_match: The string to match
        :return: A dictionary of the variables and their values
        """


        string_index = 0
        pattern_index = 0

        vars_dict = {}

        while pattern_index < len(self.pattern):
            try:
                while string_to_match[string_index] == " ":
                    string_index += 1
            except IndexError as e:
                raise ParserException(
                    f"Pattern {self.pattern} not found in {string_to_match}",
                    string_index,
                ) from e
            
            if self.pattern[pattern_index].type == "var":
                if pattern_index + 1 == len(self.pattern):
                    vars_dict[self.pattern[pattern_index].value] = string_to_match[
                        string_index:
                    ].lower()

                start_index = string_index

                if string_to_match[string_index] in (
                    char_pair[0] for char_pair in containment_chars
                ):
                    string_index = move_past_parenths(string_to_match, string_index)

                while (
                    pattern_index + 1 == len(self.pattern)
                    or string_to_match[
                        string_index : string_index
                        + len(self.pattern[pattern_index + 1].value)
                    ].lower()
                    != self.pattern[pattern_index + 1].value
                ):
                    string_index += 1
                    if string_index > len(string_to_match):
                        if pattern_index + 1 == len(self.pattern):
                            break
                        else:
                            raise ParserException(
                                f"Pattern {self.pattern} not found in {string_to_match}",
                                string_index,
                            )

                if string_index == start_index:
                    raise ParserException(
                        f"Pattern {self.pattern} not found in {string_to_match}",
                        string_index,
                    )

                vars_dict[self.pattern[pattern_index].value] = string_to_match[
                    start_index:string_index
                ]

            elif string_to_match[string_index:].lower().startswith(self.pattern[pattern_index].value):
                string_index += len(self.pattern[pattern_index].value)
            else:
                raise ParserException(
                    f"Pattern {self.pattern} not found in {string_to_match}",
                    string_index,
                )

            pattern_index += 1

        try:
            while string_to_match[string_index] == " ":
                string_index += 1
        except IndexError:
            return vars_dict

        raise ParserException(
            f"Pattern {self.pattern} not found in {string_to_match}",
            string_index,
        )

    def __repr__(self) -> str:
        rv = ""
        for element in self.pattern:
            if element.type == "var":
                rv += f"some {element.value} "
            else:
                rv += f"{element.value} "
        
        return rv[:-1]
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, DefinitionPattern):
            return False
        return str(self) == str(other)
        

class Function:
    def __init__(self, pattern, function, additional_args=None, additional_kwargs=None):
        self.pattern: DefinitionPattern = pattern
        self.function: Callable = function
        self.additional_args = additional_args or tuple()
        self.additional_kwargs = additional_kwargs or {}
    

def get_best_match(string_to_match: str, functions: List[Function] = UNDEFINED) -> Function:
    """
    Returns the best match for the string to match.
    :param functions: A list of functions to match
    :param string_to_match: The string to match
    :return: The best match
    """

    if functions is UNDEFINED:
        functions = __functions__

    og_string = string_to_match

    try:
        i = 0
        while i < len(string_to_match):
            for char in ("'", '"'):
                if string_to_match[i] == char:
                    i += 1
                    start = i
                    while string_to_match[i] != char:
                        i += 1
                    end = i
                    string_to_match = string_to_match[:start] + "_" + string_to_match[end:]
                    i = start + 2
                    break
            i += 1
    except IndexError:
        raise HumanSyntaxError(
            f"string literals missing closing quote in {og_string}",
        )

    for func in functions:
        try:
            func.pattern.match_vars_in(string_to_match)
            return func
        except ParserException:
            continue
    
    return UNDEFINED
