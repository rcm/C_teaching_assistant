#!/usr/bin/python3
import tabulate

"""
    3 vermelho
    2 laranja
    1 amarelo
    0 verde
    -1 azul
"""
colors = { 3:'🟥', 2:'🟧', 1:'🟨', 0:'🟩', -1:'🟦'} ## 🟪🟫

RED, ORANGE, YELLOW, GREEN, BLUE = [colors[c] for c in sorted(colors.keys(), reverse = True)]

palette = lambda x: colors[int(3 - x * 3)]

### aval. baseada em tabelas de intervalos→cor
def interv(inttab,v): 
   for (v1,v2),c in inttab:
      if v1 < v <= v2:
         return cores[c] 
   return ""

### aval. baseada em tabelas valor→cor
def dictab(tab,v): 
   return cores[tab.get(v,-1)]

def tabfun(t,funaval = None,fmt="simple"):
   if funaval is None:
       funaval = {}
   r = [ t[0] ]
   for tup in t[1:]:
      aux = tup.copy()
      for f,fun in funaval.items():
          res = fun(aux[f])
          if type(res) is bool:
              res = GREEN if res else RED
          if type(res) is float or type(res) is int and 0 <= res <= 1:
              res = palette(res)
          aux[f] = f"{res} {aux[f]}"
      r.append(aux)
   return tabulate.tabulate(r,headers="firstrow",tablefmt=fmt)


### Exemplo
if __name__ == "__main__":
    a = [
    [ "Nome Função","ciclometrix","Qualidade doc"],    ## header
    [ "func1",134,"d1"],
    [ "func2",4,"d0"],
    [ "func3",3,"d0"],
    [ "func4",89,"d3"],
    [ "func5",3,"d1"],
    ]

    intervcicl = [
    ((0,10),0),
    ((10,30),1),
    ((30,100),2),
    ((100,10000),3),
    ]

    tabdoc = { "d0": 0, "d1": 1, "d2": 3, "d3": 2, }

    ### col 1 avalia por tab intervalos
    ### col 2 avalia por tab (valor → cor)
    tabfun(a, {
    1: lambda c1: interv(intervcicl,c1),      
    2: lambda c2: dictab(tabdoc,c2), 
    }
    )

    tabfun(a, {
    1: lambda c1: interv(intervcicl,c1),      
    2: lambda c2: dictab(tabdoc,c2), 
    }, fmt = "html"
    )
