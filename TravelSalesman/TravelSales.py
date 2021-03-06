# ===================================================================== #
#                     TRAVEL SALESMAN PROBLEM                           #
# ===================================================================== #
import pyomo.environ as pyo
from pyomo.environ import *
from pyomo.opt import SolverFactory
'''
El problema del viajante de comercio es un problema de optimización 
combinatoria. Al igual que el del Set-Covering, es uno de los 21 problemas 
NP-completos de Richard Karp.

En este problema, un viajante debe pasar por todas las ciudades, minimizando
los costes del viaje.
'''

# DEFINICION DEL MODELO
# El modelo será un modelo concreto. 
m = ConcreteModel(name='Knap-sack problem')

# SETS
# Tenemos un set de ciudades y un alias de este set.
c = m.c = Set(initialize=['A', 'B', 'C', 'D', 'E', 'F'], ordered=True)
cc = m.cc = SetOf(c, ordered=True)

# Tenemos tambien una relación que nos permite decidir que ciudades están
# comunicadas con qué ciudades.
RelDic = {'A': ('B', 'D', 'F'),
          'B': ('A', 'C', 'D', 'E'),
          'C': ('B', 'D', 'E', 'F'),
          'D': ('A', 'B', 'C', 'F'),
          'E': ('B', 'C', 'F'),
          'F': ('A', 'C', 'D', 'E', 'F')}

R = m.R = Set(within=c * cc, ordered=True)
for s in RelDic:
    for ss in RelDic[s]:
        R.add((s, ss))

# PARÁMETROS
# Como parámetros, tenemos las distancias entre las ciudades. A las que no existen
# pondremos un cero.
DistDic = {}
DistList = [8, 3, 4, 8, 1, 5, 9, 1, 7, 2, 21, 3, 5, 7, 3, 9, 2, 35, 4, 21, 3, 35, 5]
for n, i in enumerate(R):
    DistDic[i] = DistList[n]

Cf = m.Cf = Param(c, cc, initialize=DistDic, default=0)

# VARIABLES
# Necesitamos una binaria que nos indique si se va de una ciudad c a una ciudad cc.
y = m.y = Var(c, cc, domain=pyo.Binary)


# RESTRICCIONES
# Hay que poner las restricciones

# - De todas las ciudades, debe llegar a una
def Llegada(m, ciudad):
    return sum(y[ciudad, cciudad] for cciudad in cc if (ciudad, cciudad) in R) == 1


R1 = m.r1 = Constraint(c, rule=Llegada)


# - A todas las ciudades, debe llegar a una.
def Ida(m, cciudad):
    return sum(y[ciudad, cciudad] for ciudad in c if (ciudad, cciudad) in R) == 1


R2 = m.r2 = Constraint(cc, rule=Ida)


# OBJETIVO
# El objetivo es minimizar la distancia recorrida.
def fobj(m):
    return sum(Cf[ciudad, cciudad] * y[ciudad, cciudad] for ciudad in c for cciudad in cc)


OBJ = m.obj = Objective(rule=fobj, sense=minimize)

# VERBATIM DE RESOLUCIÓN


opt = SolverFactory('glpk')
results = opt.solve(m)
results.write()
