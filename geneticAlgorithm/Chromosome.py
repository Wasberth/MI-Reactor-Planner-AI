from typing import NamedTuple
import random

type Chromosome = list[int]

class Parents(NamedTuple):
	parent1: Chromosome
	parent2: Chromosome

class ChromosomeHandler:

	def __init__(self, num_var: int, min:int, max:int):
		self.num_var = num_var
		self.min_lim = min
		self.max_lim = max

	def mate(self, parents:Parents, rand: random.Random) -> Chromosome:
		parent1, parent2 = parents
		if len(parent1) != len(parent2) and len(parent1) != self.num_var:
			raise Exception('Both parents must have the same amount of variables as the Chromosome Handler')
		child = [0]*self.num_var

		for i in range(self.num_var):
			if rand.randint(0, 1):
				child[i] = parent1[i]
			else:
				child[i] = parent2[i]

		return child
	
	def swapRandomAlele(self, value: Chromosome, rand: random.Random) -> Chromosome:
		if len(value) != self.num_var:
			raise Exception('The Chromosome must have the same amount of variables as the Chromosome Handler')
		
		a = rand.randint(0, self.num_var - 1)
		b = rand.randint(0, self.num_var - 1)
		value[a], value[b] = value[b], value[a]
		return value
	
	def randomizeAlele(self, value: Chromosome, rand: random.Random) -> Chromosome:
		if len(value) != self.num_var:
			raise Exception('The Chromosome must have the same amount of variables as the Chromosome Handler')
		
		a = rand.randint(0, self.num_var - 1)
		value[a] = rand.randint(self.min_lim, self.max_lim)
		return value
	
	def mutate(self, value: Chromosome, mutate_percent: float, rand:random.Random) -> Chromosome:
		if rand.random() >= mutate_percent:
			return value

		if rand.random() < 0.5:
			return self.swapRandomAlele(value, rand)
		else:
			return self.randomizeAlele(value, rand)
	
	def random_val(self, rand:random.Random) -> Chromosome:
		return [rand.randint(self.min_lim, self.max_lim) for _ in range(self.num_var)]


if __name__ == "__main__":
	ch = ChromosomeHandler(5, 0, 10)
	rand = random.Random(42)
	mutation_prob = 0.75
	size_pop = 2
	amount_children = 5
	pop = [ch.random_val(rand) for _ in range(size_pop)]
	print("Random Parents:", pop)
	children = [ch.mate(pop, rand) for _ in range(amount_children)]
	print("Children:", children)
	post_mutation = [ch.mutate(child, mutation_prob, rand) for child in children]
	print("Mutated children:", post_mutation)