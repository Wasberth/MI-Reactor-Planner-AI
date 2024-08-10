import time
import json
import numpy as np

from geneticAlgorithm.Chromosome import ChromosomeHandler, Chromosome
from geneticAlgorithm.Genetic import Genetic, tournament_selection, Evaluation
from runNodeScript import run_node_script, Parser

import argparse

owo = argparse.ArgumentParser(description='Corre el algoritmo genético para buscar una configuración óptima')

# value = 0
# size_pop = 25
# cross_percent = 0.5
# mutation_percent = 0.1
# iters = 400
# print_every = 100

owo.add_argument('-s', '--size', type=int, dest='value', default=0,
                    help='Size of the reactor\n\t0 - Small\n\t1 - Medium\n\t2 - Big\n\t3 - Extreme')
owo.add_argument('-p','--sp', '--size-population', type=int, dest='size_pop', default=25,  help='Size of the population per generation')
owo.add_argument('-c','--cp', '--cross-percent', type=float, dest='cross_percent', default=0.5, help='Probability of two parents mating')
owo.add_argument('-m','--mp', '--mutation-percent', type=float, dest='mutation_percent', default=0.1, help='Probability of a mutant son')
owo.add_argument('-n', '-i', '--iterations', '-g', '--generations', type=int, dest='iters', default=400, help='Number of generations of the genetic algorithm')
owo.add_argument('--print-every', type=int, default=-1, help='Number of generations between each info log')
owo.add_argument('--seed', type=float, default=None, help='Seed for the random number generator')
owo.add_argument('--superparent', type=int, nargs='*', default=None, help='Superparent configuration')
owo.add_argument('--save-name', type=str, default=None, help='Name of the folder to save the results')

args = owo.parse_args()
print(args)

size_pop = args.size_pop
cross_percent = args.cross_percent
mutation_percent = args.mutation_percent
iters = args.iters
print_every = args.print_every
superparent = args.superparent

value = args.value
global_value = value
save_route = lambda x: f"resultados/{f"_{args.save_name}_" if args.save_name else ""}{value}_{int(start)}/"

match value:
    case 0:
        hatch_amount = 9
    case 1:
        hatch_amount = 21
    case 2 :
        hatch_amount = 37
    case 3:
        hatch_amount = 69
    case _:
        raise Exception("Value must be between 0 and 3")

if superparent and len(superparent) != hatch_amount:
    raise Exception(f"Superparent must have {hatch_amount} elements")

def evaluate_configuration(configuration):
    # No isotopes or water
    if not any([i in range(0,19) for i in configuration]):
        return 0
    if value == 0 and any([i == 3 for i in configuration]):
        return 0
    output = run_node_script(value, configuration)

    if not output:
        raise Exception(f"Something went wrong with value {value} and configuration {configuration}")
    
    try:
        json_output = Parser(json.loads(output))
    except:
        raise Exception(f"Something went wrong while parsing json with value {value} and configuration {configuration}. Output from node:\n{output}")

    euProduced = json_output.efficiencyData.euProduced
    steamProductionValues = list(json_output.steamProduction.__dict__.values())        
    differentWaters = len(steamProductionValues) + 1
    efficiency = json_output.efficiencyData.efficiency if json_output.efficiencyData.efficiency else 0
    itemsBurned = json_output.efficiencyData.itemsBurned
    uranium235 = json_output.isotopeNet.uranium235
    uranium238 = json_output.isotopeNet.uranium238
    tritium = json_output.nuclearLiquids.tritium
    deuterium = json_output.nuclearLiquids.deuterium

    #if uranium235 < 0 or uranium238 < 0:
    #    return 0

    return (euProduced) / (2**itemsBurned)

def save_generation(population: list[Chromosome], evaluation: list[Evaluation], num_iters: int):
	with open(save_route(start) + f"gen_{num_iters}.txt", "w") as f:
		for i in range(len(population)):
			f.write(f"{population[i]} -> {evaluation[i]}\n")

test_function = evaluate_configuration

chromo = ChromosomeHandler(hatch_amount, 0, 23)
gen = Genetic(test_function, size_pop, cross_percent, mutation_percent, chromo)

start = time.time()
import os
os.makedirs(save_route(start), exist_ok=True)
seed = args.seed if args.seed else start
_, best_combination, _, _, _ = gen.run(tournament_selection, chromo.mate, iters, False, print_every, seed=seed, superparent=superparent, save_generation=save_generation)
end = time.time()

print("It took:", end-start)
print("Seed:", start)

output_json = json.loads(run_node_script(value, best_combination))
output = Parser(output_json)

print("The best combination was:", output.layout)

print("EFFICIENCY")
print(\
f"""{output.efficiencyData.euProduced} produced for
{output.efficiencyData.euFuelConsumed} of fuel consumed
Efficiency {output.efficiencyData.efficiency}
{output.efficiencyData.itemsBurned} Items Burned"""
)

print("INPUT")
if water := output.waterConsumption.water: print("Water: ", water)
if heavyWater := output.waterConsumption.heavyWater: print("Heavy Water: ", heavyWater)
if HPWater := output.waterConsumption.HPWater: print("HP Water: ", HPWater)
if HPHeavyWater := output.waterConsumption.HPHeavyWater: print("HP Heavy Water: ", HPHeavyWater)

print("OUTPUT")
if steam := output.steamProduction.steam: print("Steam: ", steam)
if heavyWaterSteam := output.steamProduction.heavyWaterSteam: print("Heavy Water Steam: ", heavyWaterSteam)
if HPSteam := output.steamProduction.HPSteam: print("HP Steam: ", HPSteam)
if HPHeavyWaterSteam := output.steamProduction.HPHeavyWaterSteam: print("HP Heavy Water Steam: ", HPHeavyWaterSteam)
if deuterium := output.nuclearLiquids.deuterium: print("Deuterium: ", deuterium)
if tritium := output.nuclearLiquids.tritium: print("Tritium: ", tritium)

print("ITEM DEPLETION")
if uranium := output.fuelRodConsumption.uranium: print("Uranium Rod: ", uranium)
if leMox := output.fuelRodConsumption.leMox: print("LE Mox Rod: ", leMox)
if leUranium := output.fuelRodConsumption.leUranium: print("LE Uranium Rod: ", leUranium)
if heMox := output.fuelRodConsumption.heMox: print("HE Mox Rod: ", heMox)
if heUranium := output.fuelRodConsumption.uranium: print("HE Uranium Rod: ", heUranium)
if invarPlate := output.itemsConsumption.invarPlate: print("Invar Plate: ", invarPlate)
if carbonPlate := output.itemsConsumption.carbonPlate: print("Carbon Plate: ", carbonPlate)
if controlRod := output.itemsConsumption.controlRod: print("Control Rod: ", controlRod)

print("ISOTOPE NET")
if uranium235 := output.isotopeNet.uranium235: print("Uranium235: ", uranium235)
if uranium238 := output.isotopeNet.uranium238: print("Uranium238: ", uranium238)
if plutonium := output.isotopeNet.plutonium: print("Plutonium: ", plutonium)

with open(f"resultados/{value}_{int(start)}.json", "w") as f:
    json.dump(output_json, f, indent=4)