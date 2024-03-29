

import subprocess, glob, tempfile, os, json
from utilities import *

def get_identifier_type(identifier):
    """
    This function tries to parse the identifier and sepparate it by words.
    It returns the kind of identifier and the words if it found any
    """
    possibilities = {
            'camelCase'     : [r'([a-z][a-z0-9]*)?([A-Z][a-z0-9]*)+', lambda s: [m.lower() for m in re.split('([A-Z][a-z]*)', s) if m]],
            'snake_case'    : [r'([a-z][a-z0-9]*(_[a-z0-9]+)+|[A-Z][A-Z0-9]*(_[A-Z0-9]+)+)', lambda s: [m.lower() for m in re.split('_|([0-9]+)', s) if m]],
            'simple'        : [r'([A-Z][A-Z0-9]*|[a-z][a-z0-9]*)', lambda s: s],
            }
    result = [p for p in possibilities if re.fullmatch(possibilities[p][0], identifier)]
    if len(result) == 2:
        return "simple", [identifier]
    if len(result) == 1:
        return result[0], possibilities[result[0]][1](identifier)
    return 'mixed', [identifier]

def get_last_contiguous_match(matches):
    m = matches.pop()
    rbeg, rend = m.span()
    result = m.group()
    while matches:
        m = matches.pop()
        beg, end = m.span()
        if end + 1 != rbeg: break
        rbeg = beg
        result = m.group() + result
    return result, rbeg, rend

def get_comment_before(filename, lineno):
    if lineno == 1: return ""
    before, fun_def = get_lines_before(filename, lineno)
    matches = sorted(
        [m for m in re.finditer(r'/\*.*?\*/', before, re.MULTILINE | re.DOTALL)] +
        [m for m in re.finditer(r'^\s*//.*$', before, re.MULTILINE)],
        key=lambda x: x.span()
    )

    if not matches: return ""
    last_comment, comment_begin, comment_end = get_last_contiguous_match(matches)
    function_begin, function_end = re.search(re.escape(fun_def), before).span()

    if comment_end + 1 == function_begin: return last_comment
    space = before[comment_end + 1: function_begin]
    if not re.search(r'\S+', space): return last_comment


def get_lines_before(filename, lineno):
    with open(filename) as F:
        lines = F.readlines()
    fun_def = lines[lineno - 1]
    before = lines[:lineno]
    before = "".join(before)
    return before, fun_def


def create_function(filename, fun, line1, line2, function_filename):
    comment = get_comment_before(filename, line1)
    with open(filename) as F:
        lines = F.readlines()
    with open(function_filename, "w") as F:
        print(*lines[line1 - 1 : line2 + 1], sep = "", file = F)
    return comment

def create_function_files(filename, functions, folder):
    info = {}
    for fun, line1, line2 in functions:
        line1, line2 = [int(x) for x  in [line1, line2]]
        name = filename.replace("/","_")
        function_filename = f"{folder}/{name}_{fun}.c"
        comment = create_function(filename, fun, line1, line2, function_filename)
        info[fun] = filename, function_filename, comment
    return info

def get_proto_args(proto):
    def sep_arg(lst):
        if "[" in lst[-1]:
            arr = lst.pop()
            arg_name = lst.pop()
            lst.append(arr)
        else:
            arg_name = lst.pop()

        return ' '.join(lst), arg_name

    poss_args = re.findall(r"\((.*?)\)", proto)
    assert len(poss_args) == 1, f"Too many parenthesis groups: {poss_args}"
    args = [sep_arg(re.findall(r'\w+|\*+|\[.*?\]', x)) for x in poss_args[0].split(",")]
    return set(args)

def parse_prototype(proto):
    if '{' in proto:
        proto = proto[ : proto.find('{')]

    def sep_arg(lst):
        if "[" in lst[-1]:
            arr = lst.pop()
            arg_name = lst.pop()
            lst.append(arr)
        else:
            arg_name = lst.pop()
        return arg_name, ' '.join(lst)

    poss_args = re.findall(r"\((.*)\)", proto)
    assert len(poss_args) == 1, f"Too many parenthesis groups: {poss_args}"
    args = [sep_arg(re.findall(r'\w+|\*+|\[.*?\]', x)) for x in poss_args[0].split(",") if x and x.strip() != "..."]
    type_and_fun = re.findall(r'\w+|\*+|\[.*?\]', proto[:proto.find('(')])
    return_type = ' '.join(type_and_fun[:-1])
    return return_type, dict(args)


def get_functions_from_file(filename, basedir, folder):
    real_filename = filename
    base_filename = filename.replace(basedir, "")
    if base_filename.startswith('/'):
        base_filename = base_filename[1:]

    with tempfile.TemporaryDirectory() as tmpdirname:
        if '/' in base_filename:
            base_dirname = os.path.dirname(base_filename)
            os.makedirs(f'{tmpdirname}/{base_dirname}', exist_ok = True)
        #filename = f'{tmpdirname}/{base_filename}'
        #output = subprocess.getoutput(f"gcc -E '{real_filename}' > '{tmpdirname}/{base_filename}'")
        output = subprocess.getoutput(f"ctags -x --c-kinds=fl '{filename}' | sort -k3,3n")
        return do_get_functions_from_file(filename, folder, output)

def do_get_functions_from_file(filename, folder, output):
    current_function = None
    functions = {}
    lines = []
    info = {}
    for line in output.splitlines():
        identifier, type, lineno, file, *rest = line.split()
        if identifier in '__bswap_32 __bswap_64 __uint16_identity __uint32_identity __uint64_identity'.split():
            continue
        if type == "function":
            return_type, args = parse_prototype(' '.join(rest))
            lines.append((identifier, lineno))
            current_function = (identifier, filename)
            functions[current_function] = {'name' : identifier}
            functions[current_function]["vars"] = []
            functions[current_function]["return"] = return_type
            functions[current_function]["args"] = dict(args)
        if type == "local":
            functions[current_function]["vars"].append(identifier)
    num_lines = subprocess.getoutput(f"wc -l '{filename}'").split()[0]
    lines.append(('___END___', num_lines))
    info = create_function_files(filename, [(F, L1, L2) for (F, L1), (_F, L2) in zip(lines[:-1], lines[1:])], folder)
    for id in info:
        F = (id, filename)
        functions[F]["filename"], functions[F]["function_filename"], functions[F]["comment"] = info[id]
        functions[F]["filetype"] = functions[F]["filename"][-1].upper()
    return functions 

def extract_all_functions(code):
    """
    Extracts information about all C functions in the directory

    Parameters
    ----------
    code
        Path to the directory containing the code

    Returns
    -------
    A dictionary with the following information:
        - The keys are the function names
        - The values are a dictionary with the following information:
            - vars      A list of the variables
            - return    The return type
            - args      A dictionary containing the arguments as keys and types as values
            - filename  The path to the filename that contains this function
            - function_filename Not useful right now
            - stats     The stats from multimetric for this function as a dictionary
    """
    c_files = glob.glob(f"{code}/**/*.c", recursive = True)
    h_files = glob.glob(f"{code}/**/*.h", recursive = True)
    all_files = h_files + c_files
    
    with tempfile.TemporaryDirectory() as tmpdirname:
        info = {}
        if h_files:
            H_files = " ".join(h_files)
            os.system(f"grep -e '#include.*\".*\.c\"' {H_files}")
        for file in all_files:
            info.update(get_functions_from_file(file, code, tmpdirname))
    
        data = json.loads(subprocess.getoutput(f"multimetric {tmpdirname}/*.c"))
        function_stats = data["files"]
        for fun in info:
            info[fun]["folder"] = code
            info[fun]["project"] = os.path.basename(code)
            info[fun]["stats"] = function_stats[info[fun]["function_filename"]]
            info[fun]["filename"] = info[fun]["filename"].replace(info[fun]["folder"], "")
            if info[fun]["filename"].startswith("/"):
                info[fun]["filename"] = info[fun]["filename"][1:]
    return info

def function_query(info, **options):
    def create_function(info, s):
        def stringify(x):
            if type(x) is str:
                x = x.replace('"', '\\"').replace("'","\\'")
                return f'r"""{x}"""'
            return str(x)
        any_id = list(info.keys())[0]
        poss = {
            **{M : (lambda M: lambda F: info.get(F)['stats'][M])(M) for M in info[any_id]['stats']},
            **{K : (lambda K : lambda F: info[F][K])(K) for K in "name folder project return args comment filename filetype".split()}}
        return lambda F: eval(''.join([stringify(poss[m](F)) if m in poss else m for m in re.split(r'(\w+)', s) if m]))

    opts = {
        'grep'      : lambda x: True,
        'transform' : lambda x: info[x],
        'header'    : options['transform'].replace("[","").replace("]","").split(","),
        'sort'      : None
    }
    options.update({k : create_function(info, v) for k, v in options.items() if type(v) is str})
    opts.update(options)
    if opts.get('functions'):
        globals().update(opts.get('functions'))

    res = [opts['transform'](Fun) for Fun, v in info.items() if opts['grep'](Fun)]
    if opts['sort'] is not None:
        res = [x[1] for x in sorted(((Fun, opts['transform'](Fun)) for Fun, v in info.items() if opts['grep'](Fun)), key = lambda x: opts['sort'](x[0]))]

    return [opts['header']] + res
