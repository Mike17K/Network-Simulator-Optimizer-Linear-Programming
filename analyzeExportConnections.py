import numpy as np
import pulp

'''
This script is used to find the shortest path between two nodes in a network.
The network is represented as a dictionary of dictionaries. The keys of the
outer dictionary are the nodes of the network. The inner dictionary contains
the nodes that are connected to the key node and the cost of the connection.
The script uses the PuLP library to solve the problem as a linear programming
problem. The script is based on the following example:
https://www.coin-or.org/PuLP/CaseStudies/a_transportation_problem.html

'''
connections ={'83.12.200.216': {'160.204.157.194': 20.0}, '160.204.157.194': {'83.12.200.216': 20.0, '196.116.12.205': 20.0, '206.122.126.4': 20.0}, '196.116.12.205': {'160.204.157.194': 20.0}, '206.122.126.4': {'160.204.157.194': 20.0, '121.186.96.234': 20.0}, '121.186.96.234': {'206.122.126.4': 20.0, '151.14.207.255': 20.0, '101.67.111.169': 20.0}, '151.14.207.255': {'121.186.96.234': 20.0}, '101.67.111.169': {'121.186.96.234': 20.0}}

start_ip = '83.12.200.216'
end_ip = '206.122.126.4'

def solve(connections, start_ip, end_ip):
    set_of_ruters = set()
    for key, value in connections.items():
        set_of_ruters.add(key)
        for key2, value2 in value.items():
            set_of_ruters.add(key2)
    
    number_of_routers = len(set_of_ruters)

    keys = list(set_of_ruters)

    default_cost = 1000000  # Set a big default cost

    costs = np.full((number_of_routers, number_of_routers), default_cost)

    for key, value in connections.items():
        for key2, value2 in value.items():
            costs[keys.index(key)][keys.index(key2)] = value2

    prob = pulp.LpProblem("Shortest Path Problem", pulp.LpMinimize)

    rows = len(costs)
    cols = len(costs[0])

    variables = [[pulp.LpVariable("x%s_%s" % (i+1, j+1), lowBound=0, upBound=1, cat='Binary') for j in range(cols)] for i in range(rows)]

    prob += pulp.lpSum([costs[i][j] * variables[i][j] for j in range(cols) for i in range(rows)])

    for i in range(rows):
        prob += pulp.lpSum([variables[i][j] for j in range(cols)]) <= 1

    for j in range(cols):
        prob += pulp.lpSum([variables[i][j] for i in range(rows)]) <= 1

    start_index = keys.index(start_ip)
    end_index = keys.index(end_ip)

    # incoming connection to a router has to have an outgoing connection
    for i in range(rows):
        if i != start_index and i != end_index:
            prob += pulp.lpSum([variables[i][j] for j in range(cols)]) == pulp.lpSum(
                [variables[j][i] for j in range(rows)])

    # comming connections to start_ip should be zero
    prob += pulp.lpSum([variables[j][start_index] for j in range(cols)]) == 0

    # outgoing connections from start_ip should be one
    prob += pulp.lpSum([variables[start_index][j] for j in range(cols)]) == 1

    # comming connections to end_ip should be one
    prob += pulp.lpSum([variables[j][end_index] for j in range(cols)]) == 1

    # outgoing connections from end_ip should be zero
    prob += pulp.lpSum([variables[end_index][j] for j in range(cols)]) == 0


    prob.solve()

    print("Minimum Cost =", pulp.value(prob.objective))
    for index, v in enumerate(prob.variables()):
        if v.varValue>0:
            print(v.name, "=", v.varValue, end=" ")
            print()
        # print(v.name, "=", v.varValue, end=" ")
        # if index % cols == cols - 1:
        #     print()
    path = [v.name for index, v in enumerate(prob.variables()) if v.varValue>0]
    for i in range(len(path)):
        path[i] = {"src": keys[int(path[i][1:].split("_")[0])-1], "dest":keys[int(path[i][1:].split("_")[1])-1]}

    return {"total_cost":pulp.value(prob.objective), "path": path}

res = solve(connections, start_ip, end_ip)
print(res)