import random
import re
import time
from msa_util import *

####### GA #######
# Genetic Algorithm
# Basic Implementation
# without any optimization.

def initPopulation(S):
    L = len(S)
    k = 1.3     # scale factor
    N = 1000      # N = population size
    l = int(k * max([len(S[j]) for j in range(L)]))

    # generate individual string randomly.
    def genIndiStr(str):
        gap_num = l - len(str)
        for k in range(gap_num):
            str_list = list(str)
            str_list.insert(random.randint(0,len(str)),'-')
            str = ''.join(str_list)
        return str
    
    # initialize population.
    population = []
    for i in range(N):
        population.append([])
        for j in range(L):
            population[i].append(genIndiStr(S[j]))
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
    child = []
    for i in range(L):
        selector = random.randint(1,2)
        if selector == 1:
            child.append(p1[i])
        else:
            child.append(p2[i])
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

def alignmentGA(S):
    L = len(S)
    population = initPopulation(S)
    pop_size = len(population)
    fitness_thres = misalpha*L*(L-1)/2*len(population[0][0])*0.6
    if L == 2: time_thres = 5
    else: time_thres = 15
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