import shutil
import os
import subprocess
import tempfile
import json
import glob
from collections import defaultdict
import weakref
import re
from utilities import *

class KeepRefs(object):
    __refs__ = defaultdict(list)

    def __init__(self):
        self.__refs__[self.__class__].append(weakref.ref(self))

    @classmethod
    def get_instances(cls):
        for inst_ref in cls.__refs__[cls]:
            inst = inst_ref()
            if inst is not None:
                yield inst


class ProgrammingLanguage(KeepRefs):
    def __init__(self, name, files):
        super().__init__()
        assert files, "No files"
        for f in files:
            assert issubclass(f, CodeFile), f"{f} is not a CodeFile"
        self.name = name
        self.extensions = {f.__extension__ for f in files}
        self.files = {f for f in files}

    @classmethod
    def get_language(cls, name):
        if name is None:
            return
        for lang in cls.get_instances():
            if lang.name.lower() == name.lower():
                return lang

    @classmethod
    def get_language_file_for(cls, filename):
        extension = '.' in filename and filename[filename.rfind('.') + 1:]
        extensions = {F.__extension__: (C, F) for C in cls.get_instances() for F in C.files}
        return extensions.get(extension)

    def __repr__(self):
        return self.name


class CodeFolder:
    def __init__(self, name, language=None):
        self.name = name
        self.language = language
        self.files = None
        self.metrics = None

    def create_function_table(self):
        self.get_files()
        tab = Table()
        rows = [{**{K: V for K, V in fun.items() if K != 'stats'}, **{K: V for K, V in fun['stats'].items()}}
                for FILE in self.files for fun in FILE.functions]
        if not rows:
            return None
        for row in rows:
            tab.add_row(**{**{'folder': self.name, **row}})
        return tab

    def get_files(self):
        with tempfile.TemporaryDirectory() as DIR:
            shutil.copytree(self.name, f"{DIR}/copy")
            self.files = self.files or [P[1](filename=f) for f in glob.glob(f"{DIR}/copy/**", recursive=True)
                                        if (P := ProgrammingLanguage.get_language_file_for(f))]
        return self.files

    def get_multimetric(self):
        with tempfile.TemporaryDirectory() as DIR:
            shutil.copytree(self.name, f"{DIR}/copy")
#           files = [P[1](filename = f, partial = True) for f in glob.glob(f"{DIR}/copy/**", recursive=True) if (P := ProgrammingLanguage.get_language_file_for(f))]
            files = [P[1](filename=f) for f in glob.glob(f"{DIR}/copy/**", recursive=True)
                     if (P := ProgrammingLanguage.get_language_file_for(f))]
            for F in files:
                F.__class__.preprocess(F.filename)
            self.metrics = json.loads(subprocess.getoutput(f"multimetric {' '.join(F.filename for F in files)}"))['files']

    def get_documentation(self):
        pass


class CodeFile:
    def __init__(self, **args):
        self.__dict__.update(args)
        required = "filename"
        assert all(arg in self.__dict__ for arg in required.split()), f"Required arguments: {required}"
        if not self.__dict__.get("partial"):
            self.get_functions()
            self.get_multimetric()

    @classmethod
    def preprocess(cls, name):
        pass

    def get_functions(self):
        res = []
        with open(self.filename) as F:
            lines = F.readlines()
        #list_functions = subprocess.getoutput(f'ctags  -x -u "{self.filename}"').splitlines()
        #funs = {ident for ident, filename, regexp, what, *where in (line.split('\t') for line in list_functions) if what == "f" and not where}
        lst = subprocess.getoutput(f'ctags -x -u "{self.filename}"').splitlines()
        line_numbers = []
        for line in lst:
            ident, what, lineno, filename, *rest = re.split(r'\s+', line)
            line_numbers.append(lineno)
            if what == 'function':
                res.append({'name': ident, 'filename': filename, 'lineno': lineno, 'definition': ' '.join(rest)})
        for n, entry in enumerate(res):
            fst, lst = int(entry['lineno']), int(res[n + 1]['lineno']) if n + 1 < len(res) else len(lines)
            entry.update({'code' : ''.join(lines[fst: lst]), 'endline' : lst, 'loc' : lst - fst})
        self.functions = res

    def get_multimetric(self):
        for entry in self.functions:
            with tempfile.NamedTemporaryFile(suffix = "." + self.__extension__) as TMP_F:
                self.create_temp_file(TMP_F.name, entry['definition'] + entry['code'])
                res = subprocess.getoutput(f"multimetric {TMP_F.name}")
                res_json = json.loads(res)
                assert len(res_json['files']) == 1
                entry['stats'] =  res_json['files'][TMP_F.name]

    def create_temp_file(self, fname, code):
        with open(fname, "w") as F:
            F.write(code)


class CFile(CodeFile):
    __extension__ = "c"
    def __init__(self, **args):
        super().__init__(**args)
    @classmethod
    def preprocess(cls, name):
        with tempfile.NamedTemporaryFile(suffix = ".c") as TEMP:
            os.system(f'gcc -E "{name}" > {TEMP.name}')
            shutil.copyfile(TEMP.name, name)

    def create_temp_file(self, fname, code):
        with open(fname, "w") as F:
            F.write(code)
        #self.__class__.preprocess(fname)

class HFile(CodeFile):
    __extension__ = "h"
    def __init__(self, **args):
        super().__init__(**args)

class PythonFile(CodeFile):
    __extension__ = "py"
    def __init__(self, **args):
        super().__init__(**args)

def stringify(x):
    if type(x) is str:
        x = x.replace('"', '\\"').replace("'", "\\'")
        return f'r"""{x}"""'
    return str(x)

def substitute(row):
    def replace_values(key):
        val = key.group()
        return stringify(row[val]) if val in row else val
    return replace_values


class Table:
    def __init__(self):
        self.headers = None
        self.rows = []
        self.colors = None

    def __add__(self, other):
        assert isinstance(other, Table)
        assert set(self.headers) == set(other.headers)
        tab = Table()
        tab.headers = self.headers
        tab.rows = self.rows + other.rows
        return tab

    def add_to_environ(self, dic):
        globals().update(dic)

    def get_environ(self):
        return globals()

    def add_row(self, **args):
        row_headers = [K for K in args.keys()]
        if self.headers is None:
            self.headers = row_headers
        assert set(self.headers) == set(row_headers), f"Problem adding {args} to the table. Headers {self.headers} != {row_headers}"
        self.rows.append(args)

    def select(self, condition):
        self.rows = [row for row in self.rows if eval(re.sub(r'\w+', substitute(row), condition), self.get_environ())]

    def transform(self, headers):
        self.rows = [{K : row[K] if K in row else eval(re.sub(r'\w+', substitute(row), K), self.get_environ()) for K in headers}
            for row in self.rows]
        self.headers = headers

    def rename(self, headers):
        assert len(self.headers) == len(headers), f"Different sizes {len(self.headers)} != {len(headers)}"
        self.rows = [{K2: V for (K1, V), K2 in zip(row.items(), headers)} for row in self.rows]
        self.headers = headers

    def sort(self, headers):
        self.rows = sorted(self.rows, key = lambda R : [eval(re.sub(r'\w+', substitute(R), K), self.get_environ()) for K in headers])

    def color_by(self, colors):
        self.colors = {self.headers.index(K): V for K, V in colors.items()}

    def group_by(self, headers, aggreg):
        tbl = {}
        for row in self.rows:
            grp = tuple(eval(re.sub(r'\w+', substitute(row), K), self.get_environ()) for K in headers)
            if grp not in tbl:
                tbl[grp] = {}
            for K, V in row.items():
                tbl[grp][K] = tbl[grp].get(K, []) + [V]
        res = Table()
        for grp, grp_val in tbl.items():
            row = {K: V for K, V in zip(headers, grp)}
            for agg in aggreg:
                row[agg] = eval(re.sub(r'\w+', substitute(grp_val), agg), self.get_environ())
            res.add_row(**row)
        self.headers = res.headers
        self.rows = res.rows
    def tabulate(self, format = None):
        return tabfun.tabfun([self.headers] + [[row[K] for K in self.headers] for row in self.rows],
                             funaval = self.colors, fmt = format)

    def from_json(self,  filename):
        with open(filename) as F:
            self.headers, self.rows = json.load(F)

    def to_json(self, filename=None):
        if filename is not None:
            with open(filename, 'w') as F:
                json.dump([self.headers, self.rows], F)
        else:
            json.dumps([self.headers, self.rows])


PythonLanguage = ProgrammingLanguage("Python",[PythonFile])
CLanguage = ProgrammingLanguage("C", [HFile, CFile])

