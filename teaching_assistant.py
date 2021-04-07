#!/usr/bin/python3


"""
camelCase
snake_case
"""

import sys, subprocess, glob, tempfile, os, json

def extract_functions(filename, functions, folder):
    info = {}
    for fun, line1, line2 in functions:
        num_lines = int(line2) - int(line1)
        name = filename.replace("/","_")
        function_filename = f"{folder}/{name}_{fun}.c"
        os.system(f"tail +{line1} {filename} | head -{num_lines} > {function_filename}")
        info[fun] = filename, function_filename
    return info

def get_functions(filename, folder):
    output = subprocess.getoutput(f"ctags -x --c-kinds=fl '{filename}' | sort -k3,3n")
    current_function = None
    functions = {}
    lines = []
    print(filename)
    info = {}
    for line in output.splitlines():
        identifier, type, lineno, file, *rest = line.split()
        #print(identifier, type, lineno, file, " ".join(rest), sep = "\t")
        if type == "function":
            lines.append((identifier, lineno))
            current_function = identifier
            functions[current_function] = {}
            functions[current_function]["vars"] = []
        if type == "local":
            functions[current_function]["vars"].append(identifier)
    num_lines = subprocess.getoutput(f"wc -l '{filename}'").split()[0]
    lines.append(('___END___', num_lines))
    info = extract_functions(filename, [(F, L1, L2) for (F, L1), (_F, L2) in zip(lines[:-1], lines[1:])], folder)
    for F in info:
        functions[F]["filename"], functions[F]["function_filename"] = info[F]
    return functions 

code=sys.argv[1]
c_files = glob.glob(f"{code}/**/*.c", recursive = True)
h_files = glob.glob(f"{code}/**/*.h", recursive = True)

with tempfile.TemporaryDirectory() as tmpdirname:
    info = {}
    if h_files:
        H_files = " ".join(h_files)
        os.system(f"grep -e '#include.*\".*\.c\"' {H_files}")
    for file in c_files:
        info.update(get_functions(file, tmpdirname))

    data = json.loads(subprocess.getoutput(f"multimetric {tmpdirname}/*.c"))
    function_stats = data["files"]
    for fun in info:
        info[fun]["stats"] = function_stats[info[fun]["function_filename"]]
