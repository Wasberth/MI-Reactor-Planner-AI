import time
import json
import numpy as np

from geneticAlgorithm.Chromosome import ChromosomeHandler
from geneticAlgorithm.Genetic import Genetic, tournament_selection
from runNodeScript import run_node_script, Parser

value = 0

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

size_pop = 25
cross_percent = 0.5
mutation_percent = 0.1
iters = 400
print_every = 100

def evaluate_configuration(configuration):
    output = run_node_script(value, configuration)

    if not output:
        raise Exception(f"Something went wrong with value {value} and configuration {configuration}")
    
    try:
        json_output = Parser(json.loads(output))
    except:
        raise Exception(f"Something went wrong while parsing json with value {value} and configuration {configuration}. Output from node:\n{output}")
    
    try:
        steamProductionValues = list(json_output.steamProduction.__dict__.values())        
        steamProduction = np.average(steamProductionValues)
        differentWaters = len(steamProductionValues) + 1
        efficiency = json_output.efficiencyData.efficiency
        itemsBurned = json_output.efficiencyData.itemsBurned
        uranium235 = json_output.isotopeNet.uranium235
        uranium238 = json_output.isotopeNet.uranium238

        #if uranium235 < 0 or uranium238 < 0:
        #    return 0
    except AttributeError:
        print(json_output)

    return (steamProduction * efficiency) / (2**itemsBurned * differentWaters)


test_function = evaluate_configuration

chromo = ChromosomeHandler(hatch_amount, 0, 23)
gen = Genetic(test_function, size_pop, cross_percent, mutation_percent, chromo)

start = time.time()
_, best_combination, _, _, _ = gen.run(tournament_selection, chromo.mate, iters, False, print_every, start)
end = time.time()

print("It took:", end-start)
print("Seed:", start)

output = Parser(json.loads(run_node_script(value, best_combination)))

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
