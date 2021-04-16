#!/usr/bin/python3

import io
import re
import sys
import argparse
import tabfun
from teaching_assistant import function_query, extract_all_functions
from utilities import *

def substitute_report(info, report_filename):
    with open(report_filename) as F:
        everything = F.read()
    functions = {}
    def run_query(lines):
        nonlocal info
        nonlocal functions
        globals().update(functions)
        if len(lines) > 6 and lines[:6].lower() == "python":
            exec(lines[6:].strip(), functions)
            return ""
        return query(info, lines = lines, functions = functions)
    print(re.sub(r'```(.*?)```',  lambda x: run_query(x.group(1)), everything, flags=re.S))




def query(info, lines = None, functions = None, fmt = "simple"):
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
    keywords = {
            'HEADER'            : 'header',
            'COND'              : 'grep',
            'CONDITION'         : 'grep',
            'SHOW'              : 'transform',
            'SORT'              : 'sort',
            'COLOR'             : 'color',
            'GROUP_BY'          : 'group_by',
            'AGGREG'            : 'aggregate',
            'AGGREGATE'         : 'aggregate',
            'FILE'              : 'file',
            }
    if lines is None:
        lines = sys.stdin
    elif type(lines) is str:
        lines = lines.strip().splitlines()

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

    if 'group_by' in dic:
        group_by = dic['group_by']
        del dic['group_by']
    else:
        group_by = None
    if 'aggregate' in dic:
        aggregate = dic['aggregate']
        del dic['aggregate']
    else:
        aggregate = None
    if 'transform' in dic and type(dic["transform"]) is str:
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
    if "file" in dic:
        dump_to_file = dic["file"]
        del dic["file"]
    else:
        dump_to_file = None

    if dic:
        dic['functions'] = functions
        tab = function_query(info, **dic)
        if len(tab) > 1 and group_by is not None:
            if aggregate is not None:
                afields = aggregate.split(";") if ";" in aggregate else aggregate.split()
                afields = {F : lambda x: x for F in afields}
            gfields = group_by.split()
            fields = tab[0]
            assert all(F in fields for F in gfields), f"Fields {[F for F in gfields if F not in fields]} do not belong to the table"
            F_idx = [fields.index(F) for F in gfields]
            res = {}
            for L in tab[1:]:
                key = tuple(L[I] for I in F_idx)
                if key not in res:
                    res[key] = {F : [] for F in fields if F not in gfields}
                for F in res[key].keys():
                    res[key][F].append(L[fields.index(F)])
            tab = [gfields + list(afields.keys())]
            for K, V in res.items():
                row = list(K)
                for A in afields:
                    with io.StringIO() as output:
                        print(*[V[N] if N in V.keys() else N for N in re.split(r'(\w+)', A)], file = output)
                        row.append(eval(output.getvalue()))
                tab.append(row)

        tab = tabfun.tabfun(tab, color_fun, fmt = fmt)
        if dump_to_file is not None:
            with open(dump_to_file, "w") as DUMP:
                print(tab, file = DUMP)
        return tab

if __name__ == "__main__":
    info = {}
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', nargs = 1, type = str, help='report file using templates')
    parser.add_argument('project_folder', type = str, nargs='+', help='project folder')
    args = parser.parse_args()
    for folder in args.project_folder:
        info.update(extract_all_functions(folder))
    if args.r is not None:
        for report_filename in args.r:
            substitute_report(info, report_filename)
    else:
        while True:
            print("\nInsert query:")
            result = query(info)
            if result: print(result)
