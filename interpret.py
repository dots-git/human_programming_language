class fn:
    def __init__(self, function, *args):
        self.function = function
        self.pre_args = args
    
    def run(self, *args):
        return self.function(*self.pre_args, *args)

special_chars = [" ", ".", ":"]

curr_args = []


def to_num(a):
    if isinstance(a, (int, float)):
        return float(a)
    elif isinstance(a, str):
        if a.isnumeric():
            return int(a)
        else:
            result = word_to_number(a)
            if result is None:
                raise Exception("Numeric argument required")
            return result
            

numwords = {}

units = [
        "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
        "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
        "sixteen", "seventeen", "eighteen", "nineteen",
      ]

tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

scales = ["hundred", "thousand", "million", "billion", "trillion", "quadrillion", "quintillion", "sextillion", "septillion", "octillion", "nonillion"]

numwords["and"] = (1, 0)
numwords["a"] = (1, 1)
for idx, word in enumerate(units):    numwords[word] = (1, idx)
for idx, word in enumerate(tens):     numwords[word] = (1, idx * 10)
for idx, word in enumerate(scales):   numwords[word] = (10 ** (idx * 3 or 2), 0)

def word_to_number(textnum: str):
    current = result = 0
    for word in textnum.split():
        if word not in numwords:
          return None

        scale, increment = numwords[word]
        current = current * scale + increment
        if scale > 100:
            result += current
            current = 0

    return result + current


def add(*args):
    nums = [to_num(a) for a in args]
    return sum(nums)


name_assoc = {
    ("print out", "print"): fn(print),
    ("word .", "words .*", "the words .*"): fn(str),
    "add ,*": fn(add, "#current"),
    "add up ,*": fn(add),
    "and": None,
    "some": None,
    "means": None,
}


def tokenize(code: str) -> "list[str]":
    tokens = []

    lines = code.splitlines()
    indent_amt = []

    for line in lines:
        indent = 0
        i = 0

        while i < len(line):
            if line[i] == " ":
                indent += 1
            elif line[i] == "\t":
                indent += 4
            else:
                break
            i += 1
        indent_amt.append(indent)
    if code.endswith("\n"):
        indent_amt.append(0)

    print(indent_amt)

    index = 0
    token_start = 0
    line_num = 0

    while index < len(code):
        if code[index] in special_chars:
            if index - token_start > 0:
                tokens.append(code[token_start:index])
            token_start = index + 1
            tokens.append(code[index])
        if code[index] == "\n":
            if index - token_start > 0:
                tokens.append(code[token_start:index])
            this_indent = indent_amt[line_num]
            next_indent = indent_amt[line_num + 1]
            indent_diff = next_indent - this_indent
            tokens.append(f"\n{indent_diff}")
            token_start = index + 1
            line_num += 1
        if index == len(code) - 1:
            if index - token_start + 1 > 0:
                tokens.append(code[token_start : index + 1])

        index += 1
    return tokens


def filter_names(code: str):
    tokens = tokenize(code)
    print(tokens)

    names = [key for key in name_assoc.keys()]

    name_list = []

    t = 0
    while t < len(tokens):
        potential_names: "list[list[str]]" = []
        for n in range(len(names)):
            n_name = names[n].split(" ")
            k = 0
            potential_names.append([])
            while (
                k < len(n_name)
                and t + k < len(tokens)
                and n_name[k] == tokens[t + k].lower()
            ):
                print(n_name, k)
                potential_names[n].append(n_name[k])
                k += 1
                while k < len(n_name) and t + k < len(tokens) and tokens[t + k] == " ":
                    tokens.pop(t + k)
        chosen_name = []
        for name in potential_names:
            if len(name) > len(chosen_name):
                chosen_name = name
        if len(chosen_name) > 0:
            while (
                len(name_list) > 0
                and name_list[len(name_list) - 1][0] == 3
                and name_list[len(name_list) - 1][1].endswith(" ")
            ):
                name_list[len(name_list) - 1][1] = name_list[len(name_list) - 1][1][
                    : len(name_list[len(name_list) - 1][1]) - 1
                ]
            name_list.append([0, chosen_name])
            t += len(chosen_name)
        else:
            if (
                len(name_list) > 0
                and name_list[len(name_list) - 1][0] == 3
                and not tokens[t].startswith("\n")
            ):
                name_list[len(name_list) - 1][1] += tokens[t]
                print("Adding to existing name")
            elif tokens[t].startswith("\n"):
                name_list.append([1, int(tokens[t][1:])])
                print("Adding linebreak")
            elif not tokens[t] in special_chars:
                name_list.append([3, tokens[t]])
                print("Adding new name")
            elif tokens[t] != " ":
                name_list.append([2, tokens[t]])
                print("Adding special character token")
            t += 1
    return name_list


# print(filter_names(open("example.program", "r").read()))
nums = ["one", "two", "three", "four", "one septillion"]
print([to_num(a) for a in nums])

add_func = fn(add)

print(add_func.run(*nums))