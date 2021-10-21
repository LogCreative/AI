import numpy as np
from msa_util import *

####### NDP #######

# move will be encoded as binary, support up to 8 strings comparsion.
# REMEMBER: the dimension has len + 1 length!

def editDistanceNDP(S,dist:np.array=np.array([]),move:np.array=np.array([])):
    L = len(S)
    if L == 0:
        return np.array([0]), np.array([0])
    global fdim
    if len(dist)==0:
        # initialize dist and move
        shape = tuple(len(S[l])+1 for l in range(L))
        dist = np.ones(shape=shape, dtype=np.int32)
        dist = -1 * dist        # negative means no data
        move = np.zeros(shape=shape, dtype=np.uint8)
        fdim = L
    # calculate the lower dimension (edges)
    for s in range(L):
        slicer = tuple(0 if i==s else slice(None) for i in range(L)) # slice(None) stands for : symbol
        dist[slicer], move[slicer] = editDistanceNDP(S[0:s]+S[s+1:L], dist[slicer], move[slicer]) # skip S[s]
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
            penalty = comparelist([S[a][p] if move_vec[a]==1 else "-" for a,p in enumerate(prev_pos)]+["-" for i in range(fdim - L)])  # the term is required since the higher dim will be gapped.
            moved_dist = dist[prev_pos] + penalty
            if moved_dist < minvalue:
                minmove = m
                minvalue = moved_dist
        it[0] = minvalue
        move[pos] = minmove
        it.iternext()
    return dist, move
