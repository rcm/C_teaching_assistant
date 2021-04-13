import subprocess, re, tempfile, json
import pprint

class ProgrammingLanguage:
    def __init__(self, files):
        assert files, "No files"
        for f in files: assert issubclass(f, CodeFile), f"{f} is not a CodeFile"
        self.files = files

class CodeFolder:
    def __init__(self, name, language):
        self.name = name

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
    def __init__(self, **args):
        self.extension = "c"
        super().__init__(**args)

class HFile(CodeFile):
    def __init__(self, **args):
        self.extension = "h"
        super().__init__(**args)

class PythonFile(CodeFile):
    def __init__(self, **args):
        self.extension = "py"
        super().__init__(**args)
