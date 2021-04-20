import tabfun
import re
import statistics
from consult_files import *

if False:
    T = None
    for folder in glob.glob("/home/rui/repos/LCC*") + glob.glob("/home/rui/repos/MIEI*"):
        if T is None:
            T = CodeFolder(folder).create_function_table()
        else:
            tab = CodeFolder(folder).create_function_table()
            if tab:
                T = T + tab
    T.to_json("cached_results.json")
else:
    T = Table()
    T.from_json("cached_results.json")


def col_CC(x):
    if x < 10: return tabfun.GREEN
    if x < 20: return tabfun.ORANGE
    if x < 30: return tabfun.YELLOW
    return tabfun.RED
def col_MI(x):
    if x > 80: return tabfun.GREEN
    if x > 60: return tabfun.ORANGE
    if x > 40: return tabfun.YELLOW
    return tabfun.RED

def col_BP(x):
    if x < 0.05: return tabfun.GREEN
    if x < 0.01: return tabfun.ORANGE
    if x < 0.1: return tabfun.YELLOW
    return tabfun.RED

def iqm(values, pos = 2):
    q = min(values), *statistics.quantiles(values), max(values)
    return statistics.mean([x for x in values if q[pos - 1] <= x <= q[pos + 1]])

T.add_to_environ(globals())
T.transform('folder.replace("/home/rui/repos/","") name re.sub(r"^/tmp/tmp.*?/copy/","",filename) cyclomatic_complexity loc maintainability_index halstead_bugprop'.split())
T.rename("folder name filename CC loc MI BP".split())
T.sort("folder MI -CC -loc filename name".split())
#T.select("MI < 80 or CC > 10 or BP > 0.05")
T.transform("folder name filename CC MI BP".split())
T.color_by({'CC' : scale_lower(10,80), 'MI' : scale_upper(0, 80), 'BP' : scale_lower(0.05,0.1)})
T.color_by({})

with open("problemas.md", "w") as F:
    print(T.tabulate(), file = F)

T.group_by("folder".split(), ["len(CC)", "round(100 * sum(x < 10 for x in CC)/len(CC),2)", "max(CC)",  "iqm(CC,3)", "round(100*sum(x > 80 for x in MI)/len(MI),2)", "min(MI)", "iqm(MI,1)"])
T.rename(["folder", "tam", "good_CC", "wrst_CC", "iqm_CC", "good_MI", "wrst_MI", "iqm_MI"])
T.transform(["folder", "wrst_CC", "iqm_CC", "wrst_MI", "iqm_MI", "round(100 * scale_lower(10,80)(wrst_CC), 2)", "round(100 * scale_upper(10,80)(wrst_MI), 2)"])
T.rename(["Grupo", "CC", "qCC", "MI", "qMI", "grdCC", "grdMI"])
T.transform(["Grupo", "CC", "MI"])
T.color_by({'CC' : scale_lower(10,80), 'MI' : scale_upper(0, 80)})
T.color_by({})
#T.select('folder == "MIEIPL2G01"')

with open("aval_funcoes.csv", "w") as F:
    print(re.sub(r'[ \t]+', ',', T.tabulate(format = "tsv")), file = F)