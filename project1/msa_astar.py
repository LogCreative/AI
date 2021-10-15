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

####### A* ########

def alignmentDP(S):
    L = len(S)
    S = ["-"+S[i] for i in range(L)]
    pos = [0 for i in range(L)]
    cost = 0
    output=["" for i in range(L)]
    finish = tuple(len(S[i])-1 for i in range(L))
    av_moves = [()]
    for l in reversed(range(L)):
        av_moves = [(d,)+u 
            for d in range(0,2) 
            for u in av_moves]
    av_moves = av_moves[1:]
    while not pos == finish:
        minmove = tuple(0 for i in range(L))
        mincost = math.inf
        mineval = math.inf
        for av_move in av_moves:
            n = tuple(a+b for a,b in zip(pos,av_move))
            if True in tuple(n[i]>=len(S[i]) for i in range(L)):
                continue
            a = [len(S[i])-n[i] for i in range(L)]
            h = delta * (L*max(a)-sum(a))
            # sum([abs(a[i]-a[j]) for i in range(L) for j in range(i+1,L)])
            c = comparelist([S[s][char] if av_move[s]==1 else "-" for s,char in enumerate(n)])
            f = cost + c + h
            if f < mineval:
                minmove = av_move
                mincost = c
                mineval = f
        pos = tuple(a+b for a,b in zip(pos,minmove))
        output = [output[i]+((S[i][char]) if minmove[i]==1 else "-") for i,char in enumerate(pos)]
        cost = cost + mincost
    return output, cost

output, cost = alignmentDP(["AABAA","BBBC","BBAA"])
print('\n'.join(output))
print(cost)

# Cross check
with tqdm(total=len(pqs)*len(targets), desc="Starting Up", leave=True, unit='str') as pbar:
    with open(curdir + "astar_pq.txt","w") as of:
        for pq in pqs:
            minindex = 0
            mincosting = math.inf
            for d,tg in enumerate(targets):
                pbar.set_description('Process: ' + pq[:10] + ' & ' + tg[:10])
                S = [pq,tg]
                output,pcost = alignmentDP(S)
                if pcost < mincosting:
                    minindex = d
                    mincosting = pcost
                pbar.update(1)
            minalign, _ = alignmentDP([pq,targets[minindex]])
            of.write('\n'.join(minalign))
            of.write('\n'+str(mincosting)+"\n\n")
    pbar.set_description("Finish")