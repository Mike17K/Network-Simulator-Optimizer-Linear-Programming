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
connections = {'197.57.171.215': {'89.96.185.237': 20.0, '190.136.214.174': 20.0, '13.1.98.146': 20.0}, '89.96.185.237': {'197.57.171.215': 20.0, '13.1.98.146': 20.0}, '190.136.214.174': {'197.57.171.215': 20.0, '13.1.98.146': 20.0, '175.236.177.82': 20.0}, '13.1.98.146': {'197.57.171.215': 20.0, '89.96.185.237': 20.0, '190.136.214.174': 20.0}, '175.236.177.82': {'190.136.214.174': 20.0, '49.52.132.173': 
20.0}, '49.52.132.173': {'175.236.177.82': 20.0, '58.244.111.239': 20.0, '124.245.190.41': 20.0}, '58.244.111.239': {'49.52.132.173': 20.0}, '124.245.190.41': {'49.52.132.173': 20.0}}

start_ip = '197.57.171.215'
end_ip = '49.52.132.173'

number_of_routers = len(connections.keys())
keys = list(connections.keys())

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
