import os
import numpy as np
from tqdm import tqdm

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

####### Data Preprocessing #######

curdir = os.path.dirname(__file__) + "/"

with open(curdir + "MSA_query.txt") as qf:
    queries = qf.read()
    pqs = queries[queries.find('2\n')+len('2\n'):queries.find('3\n')].splitlines()
    mqs = queries[queries.find('3\n')+len('3\n'):].splitlines()

with open(curdir + "MSA_database.txt") as df:
    targets = df.read().splitlines()

####### NDP #######

# move will be encoded as binary, support up to 8 strings comparsion.
# REMEMBER: the dimension has len + 1 length!

def decodeMove(m:np.uint8,dim):
    return tuple(1 if m & (2**v) > 0 else 0 for v in range(dim))

def editDistanceDP(S,dist:np.array=np.array([]),move:np.array=np.array([])):
    L = len(S)
    if L == 1:
        dist = np.array([i*delta for i in range(len(S[0])+1)])
        move = np.ones(shape=(len(S[0])+1), dtype=np.uint8)
        move[0] = 0  # origin is 0
        return dist, move
    if len(dist)==0:
        # initialize dist and move
        shape = tuple(len(S[l])+1 for l in range(L))
        dist = np.ones(shape=shape, dtype=np.int32)
        dist = -1 * dist        # negative means no data
        move = np.zeros(shape=shape, dtype=np.uint8)
    # calculate the lower dimension (edges)
    for s in range(L):
        slicer = tuple(0 if i==s else slice(None) for i in range(L)) # slice(None) stands for : symbol
        dist[slicer], move[slicer] = editDistanceDP(S[0:s]+S[s+1:L], dist[slicer], move[slicer]) # skip S[s]
        # configure move, insert 0 in the corresponding bit
        # Example: 4-dim xyzw xyw cube z(2) = 0, get an move 111(wyx), but with that be zero, it should be 1011.
        # REMEMBER to place the right end in the same level!
        move[slicer] = (move[slicer] >> s << (s+1)) + (move[slicer] & (2**s-1))
    # Spread the remaining space, since the edge case has been considered, the remaining space will have the same action set.
    it = np.nditer(dist, flags=['multi_index'], op_flags=["readwrite"])
    while not it.finished:
        pos = it.multi_index
        if 0 in pos:
            it.iternext()
            continue    # calculated
        ## The range of available move is 1~(2^L-1)
        minmove = np.uint8(0)
        minvalue = np.inf
        for m in range(1,2**L):
            move_vec = decodeMove(m,L)
            prev_pos = tuple(a-b for a,b in zip(pos,move_vec))
            penalty = comparelist([S[a][p] if move_vec[a]==1 else "-" for a,p in enumerate(prev_pos)])
            moved_dist = dist[prev_pos] + penalty
            if moved_dist < minvalue:
                minmove = m
                minvalue = moved_dist
        it[0] = minvalue
        move[pos] = minmove
        it.iternext()
    return dist, move

def alignmentDP(S):
    dist, move = editDistanceDP(S)

    path = []
    pos = tuple(len(s) for s in S)
    cost = dist[pos]
    start = tuple(0 for i in range(len(S)))
    while not pos == start:
        prev_move = decodeMove(move[pos],len(S))
        path.insert(0,prev_move)
        pos = tuple(a-b for a,b in zip(pos,prev_move))

    S_ = ["" for i in range(len(S))]
    for path_move in path:
        for axis,axis_move in enumerate(path_move):
            if axis_move==0:
                S_[axis] += "-"
            else:
                S_[axis] += S[axis][0]
                S[axis] = S[axis][1:]
    print(cost)
    return S_

print(alignmentDP(["AABAA","BBBC","BBAA"]))

# # Cross check
# with tqdm(total=len(pqs)*len(targets), desc="Starting Up", leave=True, unit='str') as pbar:
#     with open(curdir + "ndp_pq.txt","w") as of:
#         for pq in pqs:
#             minindex = 0
#             mincost = np.inf
#             for d,tg in enumerate(targets):
#                 pbar.set_description('Process: ' + pq[:10] + ' & ' + tg[:10])
#                 S = [pq,tg]
#                 dist,move = editDistanceDP(S)
#                 fin = tuple(len(s) for s in S)
#                 pcost = dist[fin]
#                 if pcost < mincost:
#                     minindex = d
#                     mincost = pcost
#                 pbar.update(1)
#             of.write('\n'.join(alignmentDP([pq,targets[minindex]])))
#             of.write('\n'+str(mincost)+"\n\n")
#     pbar.set_description("Finish")

# with tqdm(total=len(mqs)*len(targets)*(len(targets)-1)/2, desc="Starting Up", leave=True, unit='str') as pbar:
#     with open(curdir + "ndp_mq.txt","w") as of:
#         for mq in mqs:
#             minindex = (0,0)
#             mincost = np.inf
#             for i in range(len(targets)):
#                 for j in range(i+1,len(targets)):
#                     pbar.set_description('Process: ' + mq[:10] + ' & ' + targets[i][:10] + ' & ' + targets[j][:10])
#                     S = [mq,targets[i],targets[j]]
#                     dist,move = editDistanceDP(S)
#                     fin = tuple(len(s) for s in S)
#                     pcost = dist[fin]
#                     if pcost < mincost:
#                         minindex = (i,j)
#                         mincost = pcost
#                     pbar.update(1)
#             of.write('\n'.join(alignmentDP([mq,targets[minindex[0]],targets[minindex[1]]])))
#             of.write('\n'+str(mincost)+"\n\n")
#     pbar.set_description("Finish")