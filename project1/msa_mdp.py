import os, math
from concurrent.futures import ThreadPoolExecutor, ALL_COMPLETED, wait
from tqdm import tqdm       # pip install tqdm
import time, datetime
from msa_util import *

####### MDP #######

def editDistanceMDP(S):
    # Initialize l edges.
    # Example: 3 strings
    #     |dist[0][0][k]|  dist[0][j][0] dist[i][0][0]
    #   [[[0,2,4,6,8,...],[2],[4],...],[[2]],[[4]],...]
    # move requires to replace the number to l dim list.
    L = len(S)
    dist = []
    move = []
    for l in reversed(range(L)):
        for d in range(1 if l<L-1 else 0,len(S[l])+1):
            dist_core = (L-1) * d * delta
            move_core = ()
            for i in range(L):
                move_core = move_core + ((1 if i==l else 0),)
            for w in range(L-l-1):
                dist_core = [dist_core]
                move_core = [move_core]
            dist.append(dist_core)
            move.append(move_core)
        dist=[dist]
        move=[move]
    dist = dist[0]
    move = move[0]
    # expand the index
    index_order = [[]]
    for l in reversed(range(L)):
        index_order = [[d]+u 
            for d in range(0,len(S[l])+1) 
            for u in index_order]
    # generate avaiable moves.
    av_moves = [()]
    for l in reversed(range(L)):
        av_moves = [(d,)+u 
            for d in range(0,2) 
            for u in av_moves]
    av_moves = av_moves[1:]
    # traverse through the index_order
    # we have to consider the edge case carefully.
    for indices in index_order:
        dist_wrapper = dist
        move_wrapper = move
        for l,index in enumerate(indices):
            if index <= len(dist_wrapper) - 1:
                dist_wrapper = dist_wrapper[index]
                move_wrapper = move_wrapper[index]
            else:
                # This value is not calculated.
                # calculate the new value.
                moved_dict = {}
                for av_move in av_moves:
                    prev_node = [a-b for a,b in zip(indices, av_move)]
                    if -1 in prev_node:
                        continue        # move unaviable.
                    prev_dist = visit(dist,prev_node)
                    penalty = comparelist([S[s][c] if av_move[s]==1 else "-" for s,c in enumerate(prev_node)])
                    moved_dict[av_move] = prev_dist + penalty
                move_appender, dist_appender = min(moved_dict,key=moved_dict.get),min(moved_dict.values())

                # extend the list.
                for w in range(L-l):
                    dist_appender = [dist_appender]
                    move_appender = [move_appender]
                dist_wrapper.extend(dist_appender)                    
                move_wrapper.extend(move_appender)
    return dist,move
