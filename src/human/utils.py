from thelittlethings import to_string


containment_chars = [
    ("(", ")"),
    ("[", "]"),
    ("{", "}"),
    ("'", "'"),
    ('"', '"'),
]

def move_past_parenths(string, index):
    containment_char_count = []
    for char_pair in containment_chars:
        if string[index] == char_pair[0]:
            containment_char_count.append(1)
            continue
        elif string[index] == char_pair[1]:
            raise Exception(f"Unmatched parenthesis: {string[index]}")
        containment_char_count.append(0)
    
    while index + 1 < len(string) and any(count for count in containment_char_count):
        index += 1
        for i in range(len(containment_chars)):
            if string[index] == containment_chars[i][0]:
                containment_char_count[i] += 1
                if containment_chars[i][0] == containment_chars[i][1]:
                    if containment_char_count[i] == 2:
                        containment_char_count[i] = 0
            elif string[index] == containment_chars[i][1]:
                containment_char_count[i] -= 1
                break
        if index >= len(string):
            unmatched_parentheses = []
            for i, count in enumerate(containment_char_count):
                if count != 0:
                    unmatched_parentheses.append(f"'{containment_chars[i][0]}'")
            if len(unmatched_parentheses) == 1:
                raise Exception(f"Unmatched {unmatched_parentheses[0]}")
            else:
                raise Exception(f"Unmatched {to_string.list(unmatched_parentheses)}")

        for i, count in enumerate(containment_char_count):
            if count < 0:
                raise Exception(f"Unmatched '{containment_chars[i][1]}'")
    
    return index



def clean_outer_spaces(string_to_match: str):
    while string_to_match.endswith(" "):
        string_to_match = string_to_match[:-1]
    
    while string_to_match.startswith(" "):
        string_to_match = string_to_match[1:]

    return string_to_match

def clean_outer_parenths(string_to_match: str):
    while string_to_match.endswith(" "):
        string_to_match = string_to_match[:-1]
    
    while string_to_match.startswith(" "):
        string_to_match = string_to_match[1:]

    while len(string_to_match) > 0 and (string_to_match[0], string_to_match[-1]) in containment_chars:
        string_to_match = string_to_match[1:-1]
    
    return string_to_match

def clean_single_outer_parenths(string_to_match: str):
    if string_to_match.startswith("(") and string_to_match.endswith(")"):
        return string_to_match[1:-1], True
    else:
        return string_to_match, False