from numpy import uint8

####### Rules #######
      
delta = 2           # gap
misalpha = 3        # mismatch

def alpha(c1,c2):   # for pair-wise
    if c1==c2:
        return 0    # match
    return misalpha # mismatch

def compare(c1,c2):
    if c1==c2:
        return 0    # match
    if c1=='-' or c2=='-':
        return delta
    return misalpha # mismatch

def comparelist(cs):
    # cyclic compare
    res = 0
    for i in range(len(cs)):
        for j in range(i+1,len(cs)):
            res += compare(cs[i],cs[j])
    return res

def visit(_list, _indices):
    wrapper_ = _list
    for _index in _indices:
        wrapper_ = wrapper_[_index]
    return wrapper_

def decodeMove(m:uint8,dim):
    return tuple(1 if m & (2**v) > 0 else 0 for v in range(dim))

# not available for ga and dp
def alignment(S, editfunc):
    dist,move = editfunc(S)

    path = []
    pos = tuple(len(s) for s in S)
    start = tuple(0 for i in range(len(S)))
    while not pos == start:
        prev_move = visit(move,pos)
        if type(prev_move) == uint8:   # encoded
            prev_move = decodeMove(prev_move, len(S))
        path.insert(0,prev_move)
        pos = tuple(a-b for a,b in zip(pos,prev_move))

    S_ = ["" for i in range(len(S))]
    S_ptr = [0 for i in range(len(S))]
    for path_move in path:
        for axis,axis_move in enumerate(path_move):
            if axis_move==0:
                S_[axis] += "-"
            else:
                S_[axis] += S[axis][S_ptr[axis]]
                S_ptr[axis] += 1
    return S_