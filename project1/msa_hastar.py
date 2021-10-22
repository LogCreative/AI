import numpy as np
from queue import PriorityQueue
from msa_util import *
from msa_dp import editDistanceDP

####### HASTAR #######

def editDistanceHASTAR(S):
    L = len(S)

    # calculate the reverse before it is index-moved!
    SR = [S[i][::-1] for i in range(L)]
    pdists = []
    for i in range(L):
        for j in range(i+1, L):
            pdist, pmove = editDistanceDP(SR[i],SR[j])
            pdist.reverse()     # row reverse
            for k in range(len(pdist)):
                pdist[k].reverse()  # column reverse
            pdists.append(pdist)

    # To shift the string starting from 1
    S = ["-"+S[i] for i in range(L)]

    def h(pos:tuple):
        """
        heuristic function
        """
        hp = 0
        k = 0
        for i in range(L):
            for j in range(i+1, L):
                hp += pdists[k][pos[i]][pos[j]]
                k += 1
        return hp

    # initialize dist and move and openSet
    shape = tuple(len(S[l]) for l in range(L))
    dist = np.ones(shape=shape, dtype=np.int32)
    dist = -1 * dist        # negative means no data
    move = np.zeros(shape=shape, dtype=np.uint8)
    openSet = PriorityQueue()

    # put Start in the queue
    start = tuple(0 for l in range(L))
    dist[start] = 0
    move[start] = 0
    openSet.put((h(start),start))

    finish = tuple(len(S[l])-1 for l in range(L))
    closeSet = set()

    while not openSet.empty():
        current = openSet.get()[1]
        if current == finish:
            return dist, move
        
        closeSet.add(current)
        for m in range(1,2**L):
            move_vec = decodeMove(m,L)
            neighbor = tuple(a+b for a,b in zip(current, move_vec))
            if True in tuple(neighbor[l]>=len(S[l]) for l in range(L)):
                continue    # unavaliable move
            g = dist[current] + comparelist([S[a][p] if move_vec[a]==1 else "-" for a,p in enumerate(neighbor)])
            if dist[neighbor] == -1 or g < dist[neighbor]:
                move[neighbor] = m
                dist[neighbor] = g
                if neighbor not in closeSet:
                    openSet.put((g + h(neighbor),neighbor))

    raise Exception("unreachable.")
    