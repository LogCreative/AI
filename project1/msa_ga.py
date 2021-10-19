import os
from msa_mdp import alignmentMDP

def initPopulation(S):
    L = len(S)
    k = 10
    alignments = [[] for l in range(L)]
    for i in range(L):
        for j in range(i+1,L):
            pairAlign = alignmentMDP(S[i],S[j])
            alignments[i].append(pairAlign[0])
            alignments[j].append(pairAlign[1])
    population = []
    for i in range(k):
        population.append([])
        for j in range(L):
            population[i].append()


if __name__ == '__main__':

    ####### Data Preprocessing #######

    curdir = os.path.dirname(__file__) + "/"

    with open(curdir + "MSA_query.txt") as qf:
        queries = qf.read()
        pqs = queries[queries.find('2\n')+len('2\n'):queries.find('3\n')].splitlines()
        mqs = queries[queries.find('3\n')+len('3\n'):].splitlines()

    with open(curdir + "MSA_database.txt") as df:
        targets = df.read().splitlines()