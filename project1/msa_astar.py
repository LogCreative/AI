import os, math
import numpy as np
from tqdm import tqdm
from queue import PriorityQueue

##### Rule #####

delta = 2

def compare(c1,c2):
    if c1==c2:
        return 0    # match
    if c1=='-' or c2=='-':
        return delta
    return 3        # mismatch

def comparelist(cs):
    # cyclic compare
    res = 0
    for i in range(len(cs)):
        for j in range(i+1,len(cs)):
            res += compare(cs[i],cs[j])
    return res

####### NASTAR #######

def decodeMove(m:np.uint8,L):
    # zyx
    return tuple(1 if m & (2**v) > 0 else 0 for v in range(L))

def editDistanceASTAR(S):
    L = len(S)

    # To shift the string starting from 1
    S = ["-"+S[i] for i in range(L)]

    def h(pos:tuple):
        """
        heuristic function
        """
        a = [len(S[i])-pos[i] for i in range(L)]
        return delta * (L*max(a)-sum(a))

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
    
def alignmentASTAR(S):
    L = len(S)
    dist, move = editDistanceASTAR(S)

    path = []
    pos = tuple(len(s) for s in S)
    cost = dist[pos]
    start = tuple(0 for i in range(L))
    while not pos == start:
        prev_move = decodeMove(move[pos],L)
        path.insert(0,prev_move)
        pos = tuple(a-b for a,b in zip(pos,prev_move))

    S_ = ["" for i in range(L)]
    S_ptr = [0 for i in range(L)]
    for path_move in path:
        for axis,axis_move in enumerate(path_move):
            if axis_move==0:
                S_[axis] += "-"
            else:
                S_[axis] += S[axis][S_ptr[axis]]
                S_ptr[axis] += 1
    return S_

if __name__ == '__main__':

    ####### Data Preprocessing #######

    curdir = os.path.dirname(__file__) + "/"

    with open(curdir + "MSA_query.txt") as qf:
        queries = qf.read()
        pqs = queries[queries.find('2\n')+len('2\n'):queries.find('3\n')].splitlines()
        mqs = queries[queries.find('3\n')+len('3\n'):].splitlines()

    with open(curdir + "MSA_database.txt") as df:
        targets = df.read().splitlines()

    with tqdm(total=len(pqs)*len(targets), desc="Starting Up", leave=True, unit='str') as pbar:
        with open(curdir + "astar_pq.txt","w") as of:
            for pq in pqs:
                minindex = 0
                mincost = math.inf
                for d,tg in enumerate(targets):
                    pbar.set_description('Process: ' + pq[:10] + ' & ' + tg[:10])
                    S = [pq,tg]
                    dist,move = editDistanceASTAR(S)
                    fin = tuple(len(s) for s in S)
                    pcost = dist[fin]
                    if pcost < mincost:
                        minindex = d
                        mincost = pcost
                    pbar.update(1)
                minalign = alignmentASTAR([pq,targets[minindex]])
                of.write('\n'.join(minalign))
                of.write('\n'+str(mincost)+"\n\n")
        pbar.set_description("Finish")

    with tqdm(total=len(mqs)*len(targets)*(len(targets)-1)/2, desc="Starting Up", leave=True, unit='str') as pbar:
        with open(curdir + "ndp_mq.txt","w") as of:
            for mq in mqs:
                minindex = (0,0)
                mincost = np.inf
                for i in range(len(targets)):
                    for j in range(i+1,len(targets)):
                        pbar.set_description('Process: ' + mq[:10] + ' & ' + targets[i][:10] + ' & ' + targets[j][:10])
                        S = [mq,targets[i],targets[j]]
                        dist,move = editDistanceASTAR(S)
                        fin = tuple(len(s) for s in S)
                        pcost = dist[fin]
                        if pcost < mincost:
                            minindex = (i,j)
                            mincost = pcost
                        pbar.update(1)
                of.write('\n'.join(alignmentASTAR([mq,targets[minindex[0]],targets[minindex[1]]])))
                of.write('\n'+str(mincost)+"\n\n")
        pbar.set_description("Finish")