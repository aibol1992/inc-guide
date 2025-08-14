from numba import jit
from heapq import heappush, heappop

@jit  #ekvalentti kashiktty ansktay
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

@jit #korshiles nuktelerdi anyktau funcia
def neighbors(node, obstacles, paths):
    neighbors_list = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    result = []
    for n in neighbors_list:
        new_node = (node[0] + n[0], node[1] + n[1])
        if 0 <= new_node[1] < obstacles.shape[0] and 0 <= new_node[0] < obstacles.shape[1]:
            if paths[new_node[1], new_node[0]] == 255 and obstacles[new_node[1], new_node[0]] == 0:
                result.append(new_node)
    return result

#joldi tabu
def a_star(start, goal, obstacles, paths):
    print("START :",start," GOAL :", goal)
    start = tuple(start)
    goal = tuple(goal)
    close_set = set()
    came_from = {}
    gscore = {start: 0}
    fscore = {start: heuristic(start, goal)}
    oheap = []
    heappush(oheap, (fscore[start], start))
    while oheap:
        current = heappop(oheap)[1]
        if current == goal:
            data = []
            while current in came_from:
                data.append(current)
                current = came_from[current]
            return data
        close_set.add(current)
        for neighbor in neighbors(current, obstacles, paths):
            tentative_g_score = gscore[current] + heuristic(current, neighbor)
            if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0):
                continue
            if tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [i[1] for i in oheap]:
                came_from[neighbor] = current
                gscore[neighbor] = tentative_g_score
                fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heappush(oheap, (fscore[neighbor], neighbor))
                
    return False