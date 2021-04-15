import shutil, os
import subprocess, re, tempfile, json, glob
from collections import defaultdict
import weakref
import pprint

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
        self.extensions = {f.__extension__ for f in files}
        self.files = {f for f in files}
    @classmethod
    def get_language(cls, name):
        if name is None: return
        for lang in cls.get_instances():
            if lang.name.lower() == name.lower(): return lang
    @classmethod
    def get_language_file_for(cls, filename):
        extension = '.' in filename and filename[filename.rfind('.') + 1:]
        extensions = {F.__extension__ : (C, F) for C in cls.get_instances() for F in C.files}
        return extensions.get(extension)
    def __repr__(self):
        return self.name

class CodeFolder:
    def __init__(self, name, language = None):
        self.name = name
        self.language = language
    def get_files(self):
        self.files = [P[1](filename = f) for f in glob.glob(f"{self.name}/**", recursive=True) if (P :=ProgrammingLanguage.get_language_file_for(f))]
        print(self.files)
    def get_multimetric(self):
        with tempfile.TemporaryDirectory() as DIR:
            shutil.copytree(self.name, f"{DIR}/copy")
            files = [P[1](filename = f, partial = False) for f in glob.glob(f"{DIR}/copy/**", recursive=True) if (P :=ProgrammingLanguage.get_language_file_for(f))]
            for F in files:
                F.__class__.preprocess(F.filename)
            self.metrics = json.loads(subprocess.getoutput(f"multimetric {' '.join(F.filename for F in files)}"))
    def get_documentation(self):
        pass

class CodeFile:
    def __init__(self, **args):
        self.__dict__.update(args)
        required = "filename"
        assert all(arg in self.__dict__ for arg in required.split()), f"Required arguments: {required}"
        if self.__dict__.get("partial"):
            self.get_functions()
            self.get_multimetric()
    @classmethod
    def preprocess(cls, name):
        pass
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
            with tempfile.NamedTemporaryFile(suffix = "." + self.__extension__) as TMP_F:
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
    @classmethod
    def preprocess(cls, name):
        with tempfile.NamedTemporaryFile(suffix = ".c") as TEMP:
            os.system(f'gcc -E {name} > {TEMP.name}')
            shutil.copyfile(TEMP.name, name)
    def create_temp_file(self, fname, code):
        with open(fname, "w") as F:
            F.write(code)
        self.__class__.preprocess(fname)

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

c = CodeFolder("/home/rui/repos/MIEIPL1G02")
c.get_multimetric()
