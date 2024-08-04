from collections.abc import Callable
from typing import NamedTuple

import random
import numpy as np

from Chromosome import Chromosome, ChromosomeHandler, Parents

type Evaluation = float
class ParentIndexes(NamedTuple):
	parent1: int
	parent2: int

class Genetic:
	def __init__(self, target_fun: Callable[[Chromosome], Evaluation], size_pop: int, 
			cross_percent: float, mutation_percent: float,
			chromosomeHandler: ChromosomeHandler):
		self.f = target_fun
		self.size_pop = size_pop
		self.cross_percent = cross_percent
		self.mutation_percent = mutation_percent

		self.handler = chromosomeHandler

	def run(self, select_parents: Callable[[list[Evaluation], random.Random], list[ParentIndexes]],
			mate_parents: Callable[[Parents, random.Random], Chromosome], max_iters: int, minimizing: bool = True,
			seed: int | float | str | bytes | bytearray | None = None):

		r = random.Random(seed)
		population: list[Chromosome] = [self.handler.random_val(r) for _ in range(self.size_pop)]
		evaluation: list[Evaluation] = [self.f(p) for p in population]

		num_iters = 0

		min_found = min(evaluation)
		max_found = max(evaluation)
		min_hist = [min_found]
		max_hist = [max_found]
		avg_hist: list[Evaluation] = [np.average(evaluation)]

		while num_iters < max_iters:
			parents = select_parents(evaluation, r)
			new_gen = [mate_parents((population[parent1], population[parent2]), r) for parent1, parent2 in parents if r.random() < self.cross_percent]

			for p in new_gen:
				if r.random() < self.mutation_percent:
					p = self.handler.mutate(p, self.mutation_percent, r)

				population.append(p)
				evaluation.append(self.f(p))

			best_index = np.argsort(evaluation)
			if not minimizing:
				best_index = best_index[::-1]
			population = [population[i] for i in best_index][0:self.size_pop]
			evaluation = [evaluation[i] for i in best_index][0:self.size_pop]

			num_iters += 1
			min_found = min(min_found, evaluation[0])
			min_hist.append(min_found)
			max_hist.append(max(evaluation))
			avg_hist.append(np.average(evaluation))

		best_found = min_found if minimizing else max_found
		best_solution = population[0]

		return best_found, best_solution, min_hist, max_hist, avg_hist

def tournament_selection(evals: list[Evaluation], r: random.Random) -> list[ParentIndexes]:
	num_agents = len(evals)
	#num_agents -= num_agents % 2

	left = list(range(num_agents))
	right = list(range(num_agents))
	r.shuffle(left)
	r.shuffle(right)

	winners = [
		min([left[i], right[i]], key=lambda j: evals[j]) 
		for i in range(num_agents)
		]

	winners = [[winners[i], winners[i+1]] for i in range(0, num_agents, 2)] 
	
	return winners

if __name__ == "__main__":
	import time

	import matplotlib.pyplot as plt

	size_pop = 100
	cross_percent = 0.9
	mutation_percent = 0.1
	iters = 1000

	def squareSum(vector):
		sum = 0
		for x in vector:
			sum += x*x
		return sum

	test_function = squareSum

	chromo = ChromosomeHandler(15, 0, 100)
	gen = Genetic(test_function, size_pop, cross_percent, mutation_percent, chromo)

	start = time.time()
	best_value, best_combination, min_hist, max_hist, avg_hist = \
		gen.run(tournament_selection, chromo.mate, iters, True, start)
	end = time.time()	

	print("Se tardó ", end-start)
	print("Semilla: ", start)

	print("Mínimo encontrado:", best_value)
	print("Combinación mejor:", best_combination)
	
	x_values = range(len(min_hist))

	plt.plot(x_values, min_hist, label='Minimo')
	plt.plot(x_values, max_hist, label='Maximo')
	plt.plot(x_values, avg_hist, label='Promedio')

	plt.xlabel('X-axis')
	plt.ylabel('Y-axis')
	plt.legend()

	plt.show()
