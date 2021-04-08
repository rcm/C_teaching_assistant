#!/usr/bin/python3


"""
camelCase
snake_case
"""

import sys, subprocess, glob, tempfile, os, json, re

def create_function_files(filename, functions, folder):
    info = {}
    for fun, line1, line2 in functions:
        num_lines = int(line2) - int(line1)
        name = filename.replace("/","_")
        function_filename = f"{folder}/{name}_{fun}.c"
        os.system(f"tail +{line1} {filename} | head -{num_lines} > {function_filename}")
        info[fun] = filename, function_filename
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
            current_function = identifier
            functions[current_function] = {}
            functions[current_function]["vars"] = []
            functions[current_function]["return"] = return_type
            functions[current_function]["args"] = dict(args)
        if type == "local":
            functions[current_function]["vars"].append(identifier)
    num_lines = subprocess.getoutput(f"wc -l '{filename}'").split()[0]
    lines.append(('___END___', num_lines))
    info = create_function_files(filename, [(F, L1, L2) for (F, L1), (_F, L2) in zip(lines[:-1], lines[1:])], folder)
    for F in info:
        functions[F]["filename"], functions[F]["function_filename"] = info[F]
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

code=sys.argv[1]
info = extract_all_functions(code)
