import subprocess, re, tempfile, json, glob
from collections import defaultdict
import weakref
import pprint

def count_extensions(files):
    extensions = [f[f.rfind('.') + 1:] for f in files if '.' in f]
    return { e : extensions.count(e) for e in extensions}

def infer_language(files):
    extensions = {F : C for C in ProgrammingLanguage.get_instances() for F in C.files}
    res = {}
    for e, n in count_extensions(files).items():
        if e in extensions:
            res[extensions[e]] = res.get(extensions[e], 0) + n
    print(res)

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
        for f in files: assert issubclass(f, CodeFile), f"{f} is not a CodeFile"
        self.name = name
        self.files = {f.__extension__ for f in files}
    def __repr__(self):
        return self.name

class CodeFolder:
    def __init__(self, name, language = None):
        self.name = name
        self.language = language or infer_language(glob.glob(f"{name}/**", recursive = True))

    def get_documentation(self):
        pass

class CodeFile:
    def __init__(self, **args):
        self.__dict__.update(args)
        required = "folder filename extension"
        assert all(arg in self.__dict__ for arg in required.split()), f"Required arguments: {required}"
        self.get_functions()
        self.get_multimetric()

    def get_functions(self):
        res = []
        with open(self.filename) as F:
            lines = F.readlines()
        list_files = subprocess.getoutput(f"echo | ctags -u --filter {self.filename}").splitlines()
        funs = {id for id, finename, regexp, what, *where in (line.split('\t') for line in list_files) if what == "f" and not where}
        lst = subprocess.getoutput(f"ctags -x -u {self.filename}").splitlines()
        line_numbers = []
        for line in lst:
            id, what, lineno, filename, *rest = re.split(r'\s+', line)
            line_numbers.append(lineno)
            if id in funs:
                res.append({'name' : id, 'filename' : filename, 'lineno' : lineno, 'definition' : ' '.join(rest)})
        for n, entry in enumerate(res):
            fst, lst = int(entry['lineno']), int(res[n + 1]['lineno']) if n + 1 < len(res) else len(lines)
            entry.update({'code' : ''.join(lines[fst: lst]), 'endline' : lst, 'loc' : lst - fst})
        self.functions = res
    def get_multimetric(self):
        for entry in self.functions:
            with tempfile.NamedTemporaryFile(suffix = "." + self.extension) as TMP_F:
                self.create_temp_file(TMP_F.name, entry['code'])
                res = subprocess.getoutput(f"multimetric {TMP_F.name}")
                entry['stats'] = json.loads(res)['overall']
    def create_temp_file(self, fname, code):
        with open(fname, "w") as F:
            F.write(code)


class CFile(CodeFile):
    __extension__ = "c"
    def __init__(self, **args):
        super().__init__(**args)

class HFile(CodeFile):
    __extension__ = "h"
    def __init__(self, **args):
        super().__init__(**args)

class PythonFile(CodeFile):
    __extension__ = "py"
    def __init__(self, **args):
        super().__init__(**args)

PythonLanguage = ProgrammingLanguage("Python",[PythonFile])
CLanguage = ProgrammingLanguage("C", [HFile, CFile])

CodeFolder("/home/laboratorios/repos/MIEIPL1G02")