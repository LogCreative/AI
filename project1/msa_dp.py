import enum
import os, math
from tqdm import tqdm       # pip install tqdm
from msa_util import *

####### DP #######
# This DP method is only available for 2d
# To mainly accelerate other methods.
# which has a slightly different interface.

# Move is defined as follows
#   match_both: 0       \
#   gap_y:      1       v
#   gap_x:     -1       >

def editDistanceDP(x:str, y:str):
    dist = []
    move = []
    for i in range(len(x)+1):
        dist.append([i*delta])
        move.append([1])
    for j in range(1,len(y)+1):
        dist[0].append(j*delta)
        move[0].append(-1)
    for i in range(1,len(x)+1):
        for j in range(1,len(y)+1):
            match_both = dist[i-1][j-1] + alpha(x[i-1],y[j-1])
            gap_y = dist[i-1][j] + delta
            gap_x = dist[i][j-1] + delta

            if match_both <= gap_y:
                if match_both <= gap_x:
                    dist[i].append(match_both)
                    move[i].append(0)
                else:
                    dist[i].append(gap_x)
                    move[i].append(-1)
            else:
                if gap_x <= gap_y:
                    dist[i].append(gap_x)
                    move[i].append(-1)
                else:
                    dist[i].append(gap_y)
                    move[i].append(1)
    return dist,move

def alignmentDP(_x:str, _y:str):
    cost,move = editDistanceDP(_x,_y)

    path = []
    i, j = len(_x), len(_y)
    while not (i == 0 and j == 0):
        path.insert(0,move[i][j])
        if move[i][j] == 0:
            i -= 1
            j -= 1
        elif move[i][j] == 1:
            i -= 1
        else:
            j -= 1
    
    x_ = ""
    y_ = ""
    for m in path:
        if m==0:
            x_ += _x[0]
            y_ += _y[0]
            _x = _x[1:]
            _y = _y[1:]
        elif m==-1:
            x_ += "-"
            y_ += _y[0]
            _y = _y[1:]
        else:
            x_ += _x[0]
            _x = _x[1:]
            y_ += "-"
    return [x_,y_]