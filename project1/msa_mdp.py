import os, math
from concurrent.futures import ThreadPoolExecutor, ALL_COMPLETED, wait
from tqdm import tqdm       # pip install tqdm
import time, datetime

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

####### MDP #######

def visit(_list, _indices):
    wrapper_ = _list
    for _index in _indices:
        wrapper_ = wrapper_[_index]
    return wrapper_

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
    return visit(dist,[len(s) for s in S]),move

def alignmentMDP(S:list):
    cost,move = editDistanceMDP(S)

    path = []
    pos = [len(s) for s in S]
    start = [0 for i in range(len(S))]
    while not pos == start:
        prev_move = visit(move,pos)
        path.insert(0,prev_move)
        pos = [a-b for a,b in zip(pos,prev_move)]

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

if __name__ == '__main__':

    ####### Data Preprocessing #######

    curdir = os.path.dirname(__file__) + "/"

    with open(curdir + "MSA_query.txt") as qf:
        queries = qf.read()
        pqs = queries[queries.find('2\n')+len('2\n'):queries.find('3\n')].splitlines()
        mqs = queries[queries.find('3\n')+len('3\n'):].splitlines()

    with open(curdir + "MSA_database.txt") as df:
        targets = df.read().splitlines()

    #### 2d #####
    with tqdm(total=len(pqs)*len(targets), desc="Starting Up", leave=True, unit='str') as pbar:
        with open(curdir + "mdp_pq.txt","w") as of:
            for pq in pqs:
                minindex = 0
                mincost = math.inf
                for d,tg in enumerate(targets):
                    pbar.set_description('Process: ' + pq[:10] + ' & ' + tg[:10])
                    pcost,mov = editDistanceMDP([pq,tg])
                    if pcost < mincost:
                        minindex = d
                        mincost = pcost
                    pbar.update(1)
                of.write('\n'.join(alignmentMDP([pq,targets[minindex]])))
                of.write('\n'+str(mincost)+"\n\n")
        pbar.set_description("Finish")

    with tqdm(total=len(mqs)*len(targets)*(len(targets)-1)/2, desc="Starting Up", leave=True, unit='str') as pbar:
        with open(curdir + "mdp_mq.txt","w") as of:
            for mq in mqs:
                minindex = (0,0)
                mincost = math.inf
                for i in range(len(targets)):
                    for j in range(i+1,len(targets)):
                        pbar.set_description('Process: ' + mq[:10] + ' & ' + targets[i][:10] + ' & ' + targets[j][:10])
                        S = [mq,targets[i],targets[j]]
                        pcost,move = editDistanceMDP(S)
                        if pcost < mincost:
                            minindex = (i,j)
                            mincost = pcost
                        pbar.update(1)
                of.write('\n'.join(alignmentMDP([mq,targets[minindex[0]],targets[minindex[1]]])))
                of.write('\n'+str(mincost)+"\n\n")
        pbar.set_description("Finish")

    ### multithreaded 3d ####

    # total=len(mqs)*len(targets)*(len(targets)-1)/2
    # current = 0

    # minindex = ()
    # mincost = math.inf

    # logf = open(curdir + "mdp.log","w")
    # logf.write("Start" + '\n')
    # logf.close()

    # start = time.process_time()

    # def log(msg):
    #     global current
    #     logf = open(curdir + "mdp.log","a")
    #     logf.write('[' + str(current) + '/' + str(int(total)) + '] ' + str(datetime.timedelta(seconds=int(time.process_time() - start))) + ' ' + msg + '\n')
    #     logf.close()
    
    # def processStrings(mid, tids):
    #     global minindex,mincost,minalignment,current
    #     log(str(mid) + ' & ' + str (tids) + ' START ')
    #     pcost = editDistanceMDP([mqs[mid]]+[targets[tid] for tid in tids])[0]
    #     if pcost < mincost:
    #         minindex = tids
    #         mincost = pcost
    #     current += 1
    #     log(str(mid) + ' & ' + str (tids) + ' FINISH ' + str(pcost) + '/' + str(mincost))

    # of = open(curdir + "mdp_mq.txt",'w')
    # of.close()

    # with ThreadPoolExecutor(max_workers=8) as executer:
    #     for mid in range(len(mqs)):
    #         minindex = ()
    #         mincost = math.inf
    #         all_task = [executer.submit(processStrings, mid, [i,j]) 
    #             for i in range(len(targets)) 
    #             for j in range(i+1,len(targets))]
    #         wait(all_task, return_when=ALL_COMPLETED)
    #         of = open(curdir + "mdp_mq.txt","a")
    #         of.write('\n'.join(alignmentMDP([mqs[mid]]+[targets[tid] for tid in minindex])))
    #         of.write('\n'+str(mincost)+"\n\n")
    #         of.close()
    #     log(' ALL FINISHED! ')