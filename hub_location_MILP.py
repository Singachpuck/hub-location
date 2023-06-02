# Import PuLP modeler functions
import pandas as pd
from pulp import *

if __name__ == "__main__":

    InputData = "data/InputDataHubLargeInstance.xlsx"


    # Input Data Preparation #
    def read_excel_data(filename, sheet_name):
        data = pd.read_excel(filename, sheet_name=sheet_name, header=None)
        values = data.values
        if min(values.shape) == 1:  # This If is to make the code insensitive to column-wise or row-wise expression #
            if values.shape[0] == 1:
                values = values.tolist()
            else:
                values = values.transpose()
                values = values.tolist()
            return values[0]
        else:
            data_dict = {}
            if min(values.shape) == 2:  # For single-dimension parameters in Excel
                if values.shape[0] == 2:
                    for i in range(values.shape[1]):
                        data_dict[i + 1] = values[1][i]
                else:
                    for i in range(values.shape[0]):
                        data_dict[i + 1] = values[i][1]

            else:  # For two-dimension (matrix) parameters in Excel
                for i in range(values.shape[0]):
                    for j in range(values.shape[1]):
                        data_dict[(i + 1, j + 1)] = values[i][j]
            return data_dict

    node_num = read_excel_data(InputData, "NodeNum")[0]
    print("NodeNum: ", node_num)

    flow = read_excel_data(InputData, "flow(wij)")
    print("flow: ", flow)

    var_cost = read_excel_data(InputData, "varCost(cij)")
    print("varCost: ", var_cost)

    fixCost = read_excel_data(InputData, "fixCost(fk)")
    print("fixCost: ", fixCost)

    alpha = read_excel_data(InputData, "alpha")
    alpha = alpha[0]
    print("alpha: ", alpha)

    cap = read_excel_data(InputData, "Cap(ckmax)")
    print("Cap: ", cap)

    O = []
    for i in range(node_num):
        O.append(sum((flow[(i + 1, j + 1)] for j in range(node_num))))

    D = []
    for i in range(node_num):
        D.append(sum((flow[(j + 1, i + 1)] for j in range(node_num))))

    hub_location = LpProblem(name="hub-location", sense=LpMinimize)

    # Variables init
    Y = []
    for k in range(node_num):
        Y.append([])
        for l in range(node_num):
            Y[k].append(LpVariable('Y'+str(k)+'-'+str(l), lowBound=0, upBound=1, cat='Integer'))

    Z = []
    for k in range(node_num):
        Z.append([])
        for l in range(node_num):
            Z[k].append(LpVariable('Z'+str(k)+'-'+str(l), lowBound=0, upBound=1, cat='Integer'))

    X = []
    for i in range(node_num):
        X.append([])
        for j in range(node_num):
            X[i].append([])
            for k in range(node_num):
                X[i][j].append(LpVariable('X'+str(i)+'-'+str(j)+'-'+str(k), lowBound=0))

    # Objective function
    hub_location += lpSum([fixCost[i] * Z[i][i] for i in range(node_num)]) +\
                    lpSum([var_cost[(l + 1, j + 1)]*D[j]*Z[j][l] for j in range(node_num) for l in range(node_num)]) +\
                    lpSum([alpha*var_cost[(k + 1, l + 1)]*X[i][k][l] for i in range(node_num) for k in range(node_num) for l in range(node_num)]) +\
                    lpSum([O[i]*var_cost[(i + 1, k + 1)]*Z[i][k] for i in range(node_num) for k in range(node_num)])

    # Constraint 1
    for i in range(node_num):
        hub_location += lpSum([Z[i][k] for k in range(node_num)]) == 1

    # Constraint 2
    for k in range(node_num):
        for l in range(node_num):
            if l > k:
                hub_location += Z[k][l] + Y[k][l] <= Z[l][l]
                hub_location += Z[l][k] + Y[k][l] <= Z[k][k]

    # Constraint 3
    for i in range(node_num):
        for k in range(node_num):
            for l in range(node_num):
                if l > k:
                    hub_location += X[i][k][l] + X[i][l][k] <= O[i]*Y[k][l]

    # Constraint 4
    for i in range(node_num):
        for k in range(node_num):
            if k != i:
                hub_location += O[i]*Z[i][k] + lpSum([X[i][l][k] for l in range(node_num) if l != k]) ==\
                            lpSum([X[i][k][l] for l in range(node_num) if l != k]) + lpSum([flow[(i + 1, j + 1)]*Z[j][k] for j in range(node_num)])

    # Constraint 5
    for k in range(node_num):
        # for l in range(node_num):
        hub_location += lpSum([X[i][l][k] for i in range(node_num) for l in range(node_num) if k != l]) + lpSum([O[i]*Z[i][k] for i in range(node_num)]) <= cap[k]

    # Constraint 6
    hub_location += lpSum([Y[k][l] for k in range(node_num) for l in range(node_num)]) == lpSum([Z[k][k] for k in range(node_num)]) - 1

    hub_location.solve(PULP_CBC_CMD(msg=True))

    print(value(hub_location.objective))
