import os, math
from tqdm import tqdm       # pip install tqdm

####### Rule #######

delta = 2

def compare(c1,c2):
    if c1==c2:
        return 0    # match
    if c1=='-' or c2=='-':
        return delta
    return 3        # mismatch

####### Data Preprocessing #######

curdir = os.path.dirname(__file__) + "/"

with open(curdir + "MSA_query.txt") as qf:
    queries = qf.read()
    pqs = queries[queries.find('2\n')+len('2\n'):queries.find('3\n')].splitlines()
    mps = queries[queries.find('3\n')+len('3\n'):].splitlines()

with open(curdir + "MSA_database.txt") as df:
    targets = df.read().splitlines()

####### MDP #######

def editDistanceDP(S:list, dist = [], move= []):
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
            dist_core = d * delta
            move_core = [(1 if i==l else 0) for i in range(L)]
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
                dist_appender = 0
                move_appender = [0,0,0]

                # extend the list.
                for w in range(L-l):
                    dist_appender = [dist_appender]
                    move_appender = [move_appender]
                dist_wrapper.extend(dist_appender)                    
                move_wrapper.extend(move_appender)
    print(dist)
    print(move)

editDistanceDP(["AAAAA","BBBB","CCC"])