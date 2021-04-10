#!/usr/bin/python3


"""
Todo:
O pipeline
Ir buscar os comentários corretos

"""

import sys, subprocess, glob, tempfile, os, json, re
import tabfun

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
    comment = ""
    with open(filename) as F:
        lines = F.readlines()
    if lineno > 1:
        fun_def = lines[lineno - 1]
        before = lines[:lineno]
        before = "".join(before)
        matches = sorted(
                [m for m in re.finditer(r'/\*.*?\*/', before, re.MULTILINE | re.DOTALL)] + [m for m in re.finditer(r'^\s*//.*$', before, re.MULTILINE)],
                key = lambda x: x.span()
                )

        if matches:
            last_comment, comment_begin, comment_end = get_last_contiguous_match(matches)
            function_begin, function_end = re.search(re.escape(fun_def), before).span()

            if comment_end + 1 != function_begin:
                space = before[comment_end + 1: function_begin]
                if re.search(r'\S+', space):
                    print(space)
                else:
                    comment = last_comment
            else:
                comment = last_comment
    return comment


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

def parse_prototype(proto):
    def adjust(T, V):
        if "[" in V:
            p = V.find("[")
            return V[:p], T + V[p:]
        return V, T
    return_type, fun_name, *args = re.findall(r'\w+(?:\s*\*|\s*\[[\w\s]*\])?', proto)
    args = [adjust(T, V) for T, V in zip(args[0::2], args[1::2])]
    return return_type, args

def get_functions_from_file(filename, folder):
    output = subprocess.getoutput(f"ctags -x --c-kinds=fl '{filename}' | sort -k3,3n")
    current_function = None
    functions = {}
    lines = []
    info = {}
    for line in output.splitlines():
        identifier, type, lineno, file, *rest = line.split()
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
    
    with tempfile.TemporaryDirectory() as tmpdirname:
        info = {}
        if h_files:
            H_files = " ".join(h_files)
            os.system(f"grep -e '#include.*\".*\.c\"' {H_files}")
        for file in c_files:
            info.update(get_functions_from_file(file, tmpdirname))
    
        data = json.loads(subprocess.getoutput(f"multimetric {tmpdirname}/*.c"))
        function_stats = data["files"]
        for fun in info:
            info[fun]["stats"] = function_stats[info[fun]["function_filename"]]
    return info

def function_query(info, grep = None, transform = None, sort = None, header = None):
    def create_function(info, s):
        def stringify(x):
            if type(x) is str:
                return f'r"""{x}"""'
            return str(x)
        any_id = list(info.keys())[0]
        poss = {**{M : (lambda M: lambda F: info.get(F)['stats'][M])(M) for M in info[any_id]['stats']}, **{K : (lambda K : lambda F: info[F][K])(K) for K in "name return args comment".split()}}
        return lambda F: eval(''.join([stringify(poss[m](F)) if m in poss else m for m in re.split(r'(\w+)', s) if m]))

    if grep is None:
        grep = lambda x: True
    if transform is None:
        transform = lambda x: info[x]
    if type(grep) is str:
        grep = create_function(info, grep)
    if type(transform) is str:
        if header is None:
            header = transform.replace("[","").replace("]","").split(",")
        transform = create_function(info, transform)
    if type(sort) is str:
        sort = create_function(info, sort)

    if sort is not None:
        return [header] + [x[1] for x in sorted(((Fun, transform(Fun)) for Fun, v in info.items() if grep(Fun)), key = lambda x: sort(x[0]))]

    return [header] + [transform(Fun) for Fun, v in info.items() if grep(Fun)]

def query(info, lines = None):
    """
    Performs a query

    Parameters
    ----------
    info
        The dictionary containing all the info
    lines
        This can be a:
            None        reads from stdin
            str         should be all the input, splits into lines
            List[str]   list with all the lines in the query
    """
    keywords = { 'HEADER': 'header', 'COND' : 'grep', 'SHOW' : 'transform', 'SORT' : 'sort', 'COLOR' : 'color'}
    if lines is None:
        lines = sys.stdin
    elif type(lines) is str:
        lines = lines.splitlines()
        print(lines)

    def parser(keywords):
        dic = {}
        current_keyword = None
        current_str = ""
        def parse(L):
            nonlocal dic
            nonlocal current_keyword
            nonlocal current_str
            if not L.strip():
                if current_keyword is not None:
                    dic[keywords[current_keyword]] = current_str
                return dic
            keyword, *rest = L.split()
            if keyword == "END":
                if current_keyword is not None:
                    dic[keywords[current_keyword]] = current_str
            elif keyword in keywords:
                if current_keyword is not None:
                    dic[keywords[current_keyword]] = current_str
                current_keyword = keyword
                current_str = ' '.join(rest)
            else:
                current_str += L
            return dic
        return parse

    parse = parser(keywords)
    for L in lines:
        if not L.strip():
            parse(L)
            break
        parse(L)
    dic = parse("")
    color_fun = None
    print(dic)
    if "transform" in dic and type(dic["transform"]) is str:
        T = [x.strip() for x in dic['transform'].split(";")] if ";" in dic['transform'] else dic['transform'].split()
        if 'header' not in dic:
            dic['header'] = T
        else:
            dic['header'] = dic["header"].split()
        dic["transform"] = f"[{','.join(T)}]"
    if "sort" in dic and type(dic["sort"]) is str:
        dic["sort"] = f"[{','.join(dic['sort'].split())}]"
    if "color" in dic and type(dic["color"]) is str:
        color_fun = {dic['header'].index(K) : eval(f"lambda {K}: {V}") for K, V in [[k.strip() for k in x.split(":")] for x in dic["color"].split(";")]}
        del dic["color"]

    if dic:
        return tabfun.tabfun(function_query(info, **dic), color_fun)

if __name__ == "__main__":
	code=sys.argv[1]
	info = extract_all_functions(code)
	from utilities import *
	
	while True:
	    print("\nInsert query:")
	    result = query(info)
	    if result is None:
	        break
	    print(result)
