import random
import re
import time
from msa_util import *
from msa_dp import alignmentDP

####### GA #######

def initPopulationDP(S):
    L = len(S)
    N = 1000       # N = population size
    l = max([len(S[j]) for j in range(L)])
    x = int(l * 0.2) # max offset
    maxl = int(l * 2)

    dpaligns = [[] for k in range(L)]
    for i in range(L):
        for j in range(i+1, L):
            dpalign = alignmentDP(S[i],S[j])
            dpaligns[i].append(dpalign[0])
            dpaligns[j].append(dpalign[1])
    
    # initialize population.
    population = []
    for i in range(N):
        population.append([])
        for j in range(L):
            population[i].append("-"*random.randint(0,x)+dpaligns[j][random.randint(0,L-2)])
        population[i] = [population[i][k]+"-"*(maxl-len(population[i][k])) for k in range(L)]       # fill up
    return population

def fitness(individual):
    L = len(individual)
    l = len(individual[0])
    cost = 0
    for k in range(l):
        cost += comparelist([individual[i][k] for i in range(L)])
    return misalpha*L*(L-1)/2*l - cost  # all mismatch - current penalty

def costGA(individual):
    L = len(individual)
    l = len(individual[0])
    return misalpha*L*(L-1)/2*l - fitness(individual)

def crossover(p1, p2):
    L = len(p1)
    # horizontal crossover
    child = []
    for i in range(L):
        selector = random.randint(1,2)
        if selector == 1:
            child.append(p1[i])
        else:
            child.append(p2[i])
    # vertical crossover
    
    return child

def mutation(individual):
    # mutate the position of gap
    L = len(individual)
    mutator = random.randint(0,L-1)
    mutator_str = individual[mutator]
    gap_pos = re.findall('-',mutator_str)
    gap_pos = gap_pos[random.randint(0,len(gap_pos)-1)]
    mutator_list = list(mutator_str)
    mutator_list.remove(gap_pos)
    mutator_list.insert(random.randint(0,len(mutator_list)),'-')
    individual[mutator] = ''.join(mutator_list)
    return individual

def alignmentSGA(S):
    L = len(S)
    population = initPopulationDP(S)
    pop_size = len(population)
    fitness_thres = misalpha*L*(L-1)/2*len(population[0][0])*0.7
    if L == 2: time_thres = 5
    else: time_thres = 90
    start = time.process_time()
    same_count = 0
    prev_best = 0
    while (time.process_time()-start)<time_thres:      # set timer
        new_population = []
        pop_fitness = [fitness(individual) for individual in population]
        cur_best = max(pop_fitness)
        if cur_best>fitness_thres: break    # fitness enough
        if cur_best==prev_best: same_count += 1
        else: same_count = 0
        if same_count > 15: break   # duplicated eval, stop
        prev_best = cur_best
        for k in range(pop_size):
            p1,p2 = random.choices(population=population,weights=pop_fitness,k=2)
            child = crossover(p1,p2)
            if (random.randint(0,100)==0): child = mutation(child) # 1% mutation
            new_population.append(child)
        population = new_population
    return population[pop_fitness.index(max(pop_fitness))]