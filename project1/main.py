# Main build script.

import os, math
from tqdm import tqdm

from msa_dp import editDistanceDP
from msa_mdp import editDistanceMDP
from msa_ndp import editDistanceNDP
from msa_astar import editDistanceASTAR
from msa_hastar import editDistanceHASTAR
from msa_ga import alignmentGA, costGA
from msa_util import alignment,visit
from msa_dp import alignmentDP
from msa_sga import alignmentSGA, costSGA

def preprocessing():
    global curdir, pqs, mqs, targets
    # curdir = os.path.dirname(__file__) + "/"
    curdir = ""

    with open(curdir + "MSA_query.txt") as qf:
        queries = qf.read()
        pqs = queries[queries.find('2\n')+len('2\n'):queries.find('3\n')].splitlines()
        mqs = queries[queries.find('3\n')+len('3\n'):].splitlines()

    with open(curdir + "MSA_database.txt") as df:
        targets = df.read().splitlines()

def process2d(func, methodname):
    with tqdm(total=len(pqs)*len(targets), desc="Starting Up", leave=True, unit='str') as pbar:
        with open(curdir + methodname + "2d.txt","w") as of:
            for pq in pqs:
                minindex = 0
                mincost = math.inf
                for d,tg in enumerate(targets):
                    pbar.set_description('Process: ' + pq[:10] + ' & ' + tg[:10])
                    S = [pq,tg]
                    if methodname == "ga":
                        pcost = costGA(func(S))
                    elif methodname == "sga":
                        pcost = costSGA(func(S))
                    else:
                        dist,move = func(S[0],S[1]) if methodname=="dp" else func(S)
                        fin = tuple(len(s) for s in S)
                        pcost = visit(dist,fin)
                    if pcost < mincost:
                        minindex = d
                        mincost = pcost
                    pbar.update(1)
                if methodname == "ga" or methodname == "sga":
                    minalign = func([pq,targets[minindex]])
                elif methodname == "dp":
                    minalign = alignmentDP(pq,targets[minindex])
                else:
                    minalign = alignment([pq,targets[minindex]], func)
                of.write('\n'.join(minalign))
                of.write('\n'+str(mincost)+"\n\n")
        pbar.set_description("Finish")

def process3d(func, methodname):
    with tqdm(total=int(len(mqs)*len(targets)*(len(targets)-1)/2), desc="Starting Up", leave=True, unit='str') as pbar:
        with open(curdir + methodname + "3d.txt","w") as of:
            of.write("")
        for mq in mqs:
            minindex = (0,0)
            mincost = math.inf
            for i in range(len(targets)):
                for j in range(i+1,len(targets)):
                    pbar.set_description('Process: ' + mq[:10] + ' & ' + targets[i][:10] + ' & ' + targets[j][:10])
                    S = [mq,targets[i],targets[j]]
                    if methodname == "ga":
                        pcost = costGA(func(S))
                    elif methodname == "sga":
                        pcost = costSGA(func(S))
                    else:
                        dist,move = func(S)
                        fin = tuple(len(s) for s in S)
                        pcost = visit(dist,fin)
                    if pcost < mincost:
                        minindex = (i,j)
                        mincost = pcost
                    pbar.update(1)
            if methodname == "ga" or methodname == "sga":
                minalign = func([mq,targets[minindex[0]],targets[minindex[1]]])
            else:
                minalign = alignment([mq,targets[minindex[0]],targets[minindex[1]]],func)
            with open(curdir + methodname + "3d.txt","a") as of:
                of.write('\n'.join(minalign))
                of.write('\n'+str(mincost)+"\n\n")
        pbar.set_description("Finish")

if __name__ == '__main__':

    choosemethod = input("Input the method (dp, mdp, ndp, astar, hastar, ga, sga):")
    choosedim = input("Input the dimension for analysis (2, 3):")

    preprocessing()

    if choosemethod == "dp":
        methodfunc = editDistanceDP
        if choosedim == "3":
            raise Exception("DP is not available for 3d!")
    elif choosemethod == "mdp":
        methodfunc = editDistanceMDP
    elif choosemethod == "ndp":
        methodfunc = editDistanceNDP
    elif choosemethod == "astar":
        methodfunc = editDistanceASTAR
    elif choosemethod == "hastar":
        methodfunc = editDistanceHASTAR
    elif choosemethod == "ga":
        methodfunc = alignmentGA
    elif choosemethod == "sga":
        methodfunc = alignmentSGA

    if choosedim == "2":
        process2d(methodfunc, choosemethod)
    elif choosedim == "3":
        process3d(methodfunc, choosemethod)
    