#!/usr/bin/python3
import tabulate

cores = { 3:'🟥', 2:'🟧', 1:'🟨', 0:'🟩', -1:'🟦'} ## 🟪🟫

### aval. baseada em tabelas de intervalos→cor
def interv(inttab,v): 
   for (v1,v2),c in inttab:
      if v1 < v <= v2:
         return cores[c] 
   return ""

### aval. baseada em tabelas valor→cor
def dictab(tab,v): 
   return cores[tab.get(v,-1)]

def tabfun(t,funaval,fmt="simple"):
   r = [ t[0] ]
   for tup in t[1:]:
      aux = tup.copy()
      for f,fun in funaval.items():
          aux[f] = f"{fun(aux[f])} {aux[f]}"
      r.append(aux)
   print(tabulate.tabulate(r,headers="firstrow",tablefmt=fmt))


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
