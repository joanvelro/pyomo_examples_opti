"""
*-------------------------------------------------------------------------------
*                    #### STRIP-PACKING 2D PROBLEM ####
**------------------------------------------------------------------------------



* N.W. Sawaya, I. E. Grossmann, 2005
https://doi.org/10.1016/S1570-7946(03)80444-3

"""

"""
 PROBLEM STATMENT:
    A given set of rectangles is to be packed into a strip of fixed width W
    but unknown length L. The objective is to minimize the length of the
    strip while fitting all rectangles without overlap and without rotation.

	This is combinatorial NP-hard optimization problem.
"""
import matplotlib.pyplot as plt
from pandas import read_excel
from numpy import array, shape, vstack, append
import pyomo.environ as pyo

# Create model object
model = pyo.ConcreteModel(name="STRIP-PACKING 2D PROBLEM ")

# Read data from excel file using pandas
excel_filename = 'strip_packing_2D_data.xlsx'

sp2d_df = read_excel(excel_filename, skiprows=3, usecols='B:D', index_col=0)

# Set declarations
rectangle_i = sp2d_df.index.tolist()
I = model.I = pyo.Set(initialize=rectangle_i, ordered=True)
J = model.J = pyo.Set(initialize=rectangle_i, ordered=True)

# Problem data
# > Rectangle dimensions (Length & Height)
L = {i: sp2d_df.at[i, 'L'] for i in I}
H = {i: sp2d_df.at[i, 'H'] for i in I}

# > Total Length if all the rectangles are stacked together
L_up = sp2d_df['L'].sum()

# > Width of the strip
width_strip = sp2d_df['H'].max()
W = width_strip

# > Big-M parameters
M1 = W  # Up
M2 = 60  # Rigth
M3 = W  # Down
M4 = 60  # Left

# Variable declarations
# > Continuous Variables
lt = model.lt = pyo.Var(domain=pyo.NonNegativeReals, doc='Length of the strip')
x = model.x = pyo.Var(I, domain=pyo.NonNegativeReals, doc='x axis position')
y = model.y = pyo.Var(I, domain=pyo.NonNegativeReals, doc='y axis position')

# > Binary Variables
w1 = model.w1 = pyo.Var(I, J, domain=pyo.Binary,
                        doc='1 if rectangle j is placed above rectangle i. 0 otherwise')
w2 = model.w2 = pyo.Var(I, J, domain=pyo.Binary,
                        doc='1 if rectangle j is placed to the rigth of rectangle i. 0 otherwise')
w3 = model.w3 = pyo.Var(I, J, domain=pyo.Binary, doc='1 if rectangle j is placed below rectangle i. 0 otherwise')
w4 = model.w4 = pyo.Var(I, J, domain=pyo.Binary,
                        doc='1 if rectangle j is placed to the left of rectangle i. 0 otherwise')


# -------------------------------------------------------------------------------
# ### MODEL EQUATIONS ###
# -------------------------------------------------------------------------------

# Global Constraint.
def global_constraint_rule(model, i):
    return lt >= x[i] + L[i]


model.global_constraint = pyo.Constraint(I, rule=global_constraint_rule)


# Disjunctions. Big-M Reformulation
#   Each disjunct represents the position of rectangle i in relation to
#   rectangle j.
#   The point of  reference (xi, yi)  corresponds  to  the  upper  left
#   corner  of  every rectangle.

# > Disjunction <up>
def disjunction_up_rule(model, i, j):
    if i < j:
        return y[j] - H[j] >= y[i] - M1 * (1 - w1[i, j])
    else:
        return pyo.Constraint.Skip


model.disjunction_up = pyo.Constraint(I, J, rule=disjunction_up_rule)


# > Disjunction <right>
def disjunction_rigth_rule(model, i, j):
    if i < j:
        return x[i] + L[i] <= x[j] + M2 * (1 - w2[i, j])
    else:
        return pyo.Constraint.Skip


model.disjunction_right = pyo.Constraint(I, J, rule=disjunction_rigth_rule)


# > Disjunction <down>
def disjunction_down_rule(model, i, j):
    if i < j:
        return y[i] - H[i] >= y[j] - M3 * (1 - w3[i, j])
    else:
        return pyo.Constraint.Skip


model.disjunction_down = pyo.Constraint(I, J, rule=disjunction_down_rule)


# > Disjunction <left>
def disjunction_left_rule(model, i, j):
    if i < j:
        return x[j] + L[j] <= x[i] + M4 * (1 - w4[i, j])
    else:
        return pyo.Constraint.Skip


model.disjunction_left = pyo.Constraint(I, J, rule=disjunction_left_rule)


# Logic propositions
def logic_proposition_rule(model, i, j):
    if i < j:
        return w1[i, j] + w2[i, j] + w3[i, j] + w4[i, j] == 1
    else:
        return pyo.Constraint.Skip


model.logic_proposition = pyo.Constraint(I, J, rule=logic_proposition_rule)

# Objective function. Length of the strip
model.objective_fcn = pyo.Objective(expr=lt, sense=pyo.minimize)

# Bounds on variables
# > x-coordinate upper bound for every rectangle
x_UP = L_up

for i in I:
    x[i].setub(x_UP - L[i])

# > y-coordinate upper and lower bounds
for i in I:
    y[i].setub(W)
    y[i].setlb(H[i])

# Solver call
# pyo.SolverFactory("cbc").solve(model, tee=True)
pyo.SolverFactory("cplex").solve(model, tee=True)

# GAMS solver call
# pyo.SolverFactory('gams').solve(model, solver = 'cplex', tee = True, keepfiles=True)

# GAMS solver call with options
# pyo.SolverFactory('gams').solve(model,
#                                solver='cplex',
#                                tee=True,
#                                keepfiles=True,
#                                add_options=['option optcr = 0;', 'option optca = 0;'])

# Plot Results =================================================================
xi_array = array([])
yi_array = array([])
Li_array = array([])
Hi_array = array([])

for i in I:
    xi = x[i].value
    yi = y[i].value
    Li = L[i]
    Hi = H[i]
    xi_array = append(xi_array, xi)
    yi_array = append(yi_array, yi)
    Li_array = append(Li_array, Li)
    Hi_array = append(Hi_array, Hi)

xi_array = xi_array.reshape(1, shape(xi_array)[0])
yi_array = yi_array.reshape(1, shape(yi_array)[0])

Xi_array = vstack((xi_array, xi_array + Li_array, xi_array + Li_array, xi_array))
Yi_array = vstack((yi_array, yi_array, yi_array - Hi_array, yi_array - Hi_array))

p1 = plt.fill(Xi_array, Yi_array)
plt.show()
plt.savefig('plot.png')
