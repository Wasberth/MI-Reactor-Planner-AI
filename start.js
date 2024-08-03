const fs = require('fs')
const {value, conts} = require('minimist')(process.argv.slice(2));
const contents = conts.split(',')

/*
 * <option value="0">Small</option>
 * <option value="1">Medium</option>
 * <option value="2">Large</option>
 * <option value="3">Extreme</option>
*/
if (value < 0 || value > 4) {
    throw new Error("The value mus be between 0 and 3");
}

switch (value) {
    case 0:
        if (contents.length != 9) {
            throw new Error("For a small nuclear reactor, there must be exactly 9 contents")
        }
        break;

    case 1:
        if (contents.length != 21) {
            throw new Error("For a medium nuclear reactor, there must be exactly 21 contents")
        }
        break;

    case 2:
        if (contents.length != 37) {
            throw new Error("For a large nuclear reactor, there must be exactly 37 contents")
        }
        break;

    case 3:
        if (contents.length != 69) {
            throw new Error("For a extreme nuclear reactor, there must be exactly 69 contents")
        }
        break;
}

let size = 5 + 2 * value


const fileList = fs.readdirSync('./nuclear')
let afterImportsFunctions = []
for (const file of fileList) {
    try {
        const nuclearModule = require(`./nuclear/${file}`)
        //console.log(`Importing ${file}`)
        for (const imported of Object.keys(nuclearModule)) {
            if (imported === "afterImports") {
                afterImportsFunctions.push(nuclearModule[imported])
                continue
            }

            //console.log(`\t${imported}`)
            global[imported] = nuclearModule[imported]
        }
    } catch (error) {
        //console.log(error);
        
        fileList.push(file)
        //console.log(`Dependencies missing for ${file}`)
    }
}

afterImportsFunctions.forEach(fn => fn());

function Material (type) {
    this.type = type;
    this.isFluid = Object.values(Fluids).includes(type);
    this.component = NuclearComponent.get(type);
};

const Blocks = Object.freeze({
    CASING: Symbol('CASING'),
    HATCH: Symbol('HATCH'),
});

const format = (x, suffix='') => {
    const lookup = [
      [ 1, ""],
      [ 1e3, "k"],
      [ 1e6, "M"],
      [ 1e9, "G"],
      [ 1e12, "T"],
      [ 1e15, "P"],
      [ 1e18, "E"],
    ];
    const [value, symbol] = lookup.findLast(([value]) => x >= value) || lookup[0];
    const v = x / value;
    const digits = 3 - Math.floor(Math.log10(Math.max(1, v)));
    return `${(v).toFixed(digits)}${symbol}${suffix}`;
};

const MATERIALS = Object.values(Fluids).slice(0,4).concat(Object.values(Fuels), Object.values(Items))
    .map((type) => new Material(type));

class Map {
    constructor(value, size, items) {
        this.size = size;
        this.tiles = new Array(size * size);

        // Parece ser que esto rellena las tiles con Hatch
        let itemIndex = 0
        for (let x = 0; x < size; x++) {
            let minZ;
            let xAbs = Math.abs(x - 2 - value);
            if (value != 3) {
                minZ = (xAbs == 0) ? 0 : (xAbs - 1);
            } else {
                minZ = (xAbs <= 1) ? 0 : (xAbs - 2);
            }

            let maxZ = 2 * (2 + value) - minZ;
            for (let z = minZ; z <= maxZ; z++) {
                if (!(z == minZ || z == maxZ || xAbs == 2 + value)) {
                    this.tiles[z * size + x] = items[itemIndex++];
                }
            }
        }
    }

    getTile(col, row) {
        return this.tiles[row * this.size + col];
    }

    /**
     * Cambio de objeto Tile en la posición (col, row)
     * 
     * Se toma en cuenta si la Tile es null, en cuyo caso no se puede cambiar (así es la vida)
     * 
     * @param {number} col
     * @param {number} row
     * @param {number} tile index en el array MATERIALS
     */
    setTile(col, row, tile) {
        const oldTile = this.tiles[row * this.size + col];
        if (tile == null || oldTile == null) {
            return;
        }

        this.tiles[row * this.size + col] = newTile;
        Simulator.init(this);
    }

    /**
     * Devuelve una Tile aleatoria que no sea null
     * 
     * @returns {Array} [col, row]
     */
    chooseRandomTile () {
        let randomCol, randomRow;
        do {
            randomCol = Math.floor(Math.random() * this.size);
            randomRow = Math.floor(Math.random() * this.size);
        } while (this.getTile(randomCol, randomRow) == null);
        return [randomCol, randomRow];
    }

    /*
     * Cambia dos Tiles adyacentes aleatoriamente
    */
    randomizeContents() {
        let [randomCol, randomRow] = this.chooseRandomTile();
        let randomMaterial = Math.floor(Math.random() * MATERIALS.length);

        this.setTile(randomCol, randomRow, randomMaterial);
    }

    /**
     * Intercambia dos Tiles aleatorias
     */
    swapTiles() {
        let [col1, row1] = this.chooseRandomTile()
        let [col2, row2] = this.chooseRandomTile()

        const tile1 = this.getTile(col1, row1);
        const tile2 = this.getTile(col2, row2);

        this.setTile(col1, row1, tile2);
        this.setTile(col2, row2, tile1);
    }

    mutate(){
        if (Math.random() < 0.5) {
            this.randomizeContents()
        } else {
            this.swapTiles()
        }
    }
}

Map.prototype.toString = function () {
    //Imprimir las tiles
    let mapString = '';

    for (let row = 0; row < this.size; row++) {
        for (let col = 0; col < this.size; col++) {
            const tile = this.getTile(col, row);
            if (tile == null || !MATERIALS[tile]) {
                continue;
            }
            mapString += MATERIALS[tile].type.toString();
        }
        mapString += '\n';
    }

    return mapString;
}

let map = new Map(value, size, contents)

const Simulator = {};
global.Simulator = Simulator
Simulator.speed = 1200;
Simulator.steamOutput = true;
Simulator.historyLength = 1200;

Simulator.init = function(map) {
    const hatchesGrid = new Array(map.size * map.size).fill(null);
    map.tiles.forEach((tile, i) => {
        const materialTile = MATERIALS[tile];
        if (materialTile?.component || materialTile?.type === Blocks.HATCH) {
            hatchesGrid[i] = new NuclearHatch(materialTile.component);
        }
    });
    this.nuclearGrid = new NuclearGrid(map.size, map.size, hatchesGrid);
    this.efficiencyHistory = new NuclearEfficiencyHistoryComponent();
    this.productionHistory = new NuclearProductionHistoryComponent(Simulator.historyLength);
};

Simulator.update = function() {
    for (let i=0; i < this.speed; ++i) {
        this.nuclearGrid.hatchesGrid.forEach((hatch) => {
            if (hatch != null) {
                hatch.tick();
            }
        })
        NuclearGridHelper.simulate(this.nuclearGrid, this.efficiencyHistory, this.productionHistory);
        this.efficiencyHistory.tick();
        this.productionHistory.tick();
    }
};

Simulator.init(map)
Simulator.update();

// Esto es para imprimir los valores de producción


const waterConsumption = Simulator.productionHistory.getAverage(NuclearProductionHistoryComponentType.waterConsumption);
const heavyWaterConsumption = Simulator.productionHistory.getAverage(NuclearProductionHistoryComponentType.heavyWaterConsumption);
const highPressureWaterConsumption = Simulator.productionHistory.getAverage(NuclearProductionHistoryComponentType.highPressureWaterConsumption);
const highPressureHeavyWaterConsumption = Simulator.productionHistory.getAverage(NuclearProductionHistoryComponentType.highPressureHeavyWaterConsumption);

const steamProduction = Simulator.productionHistory.getAverage(NuclearProductionHistoryComponentType.steamProduction);
const heavyWaterSteamProduction = Simulator.productionHistory.getAverage(NuclearProductionHistoryComponentType.heavyWaterSteamProduction);
const highPressureSteamProduction = Simulator.productionHistory.getAverage(NuclearProductionHistoryComponentType.highPressureSteamProduction);
const highPressureHeavyWaterSteamProduction = Simulator.productionHistory.getAverage(NuclearProductionHistoryComponentType.highPressureHeavyWaterSteamProduction);
const deuteriumProduction = Simulator.productionHistory.getAverage(NuclearProductionHistoryComponentType.deuteriumProduction);
const tritiumProduction = Simulator.productionHistory.getAverage(NuclearProductionHistoryComponentType.tritiumProduction);

const uraniumRodConsumption = Simulator.productionHistory.getAverage(NuclearProductionHistoryComponentType.uraniumRodConsumption);
const leMoxRodConsumption = Simulator.productionHistory.getAverage(NuclearProductionHistoryComponentType.leMoxRodConsumption);
const leUraniumRodConsumption = Simulator.productionHistory.getAverage(NuclearProductionHistoryComponentType.leUraniumRodConsumption);
const heMoxRodConsumption = Simulator.productionHistory.getAverage(NuclearProductionHistoryComponentType.heMoxRodConsumption);
const heUraniumRodConsumption = Simulator.productionHistory.getAverage(NuclearProductionHistoryComponentType.heUraniumRodConsumption);

const invarPlateConsumption = Simulator.productionHistory.getAverage(NuclearProductionHistoryComponentType.invarPlateConsumption);
const carbonPlateConsumption = Simulator.productionHistory.getAverage(NuclearProductionHistoryComponentType.carbonPlateConsumption);
const controlRodConsumption = Simulator.productionHistory.getAverage(NuclearProductionHistoryComponentType.controlRodConsumption);


const addFluid = (prefix, value)  => {
    if (value > 0) {
        console.log(`${prefix}${format(value, ' mb/t')}`);
    }
};

console.log('INPUT');
addFluid('  Water                ', waterConsumption);
addFluid('  Heavy Water          ', heavyWaterConsumption);
addFluid('  HP Water             ', highPressureWaterConsumption);
addFluid('  HP Heavy Water       ', highPressureHeavyWaterConsumption);

console.log('OUTPUT');
addFluid('  Steam                ', steamProduction);
addFluid('  Heavy Water Steam    ', heavyWaterSteamProduction);
addFluid('  HP Water Steam       ', highPressureSteamProduction);
addFluid('  HP Heavy Water Steam ', highPressureHeavyWaterSteamProduction);
addFluid('  Deuterium            ', deuteriumProduction);
addFluid('  Tritium              ', tritiumProduction);

const addRod = (prefix, value)  => {
    if (value !== 0) {
        let suffix = 't';
        [
            [20, 's'],
            [60, 'min'],
            [60, 'h'],
            [24, 'day'],
        ].forEach(([mul, suf]) => {
            if (Math.abs(value) < 1) {
                value *= mul;
                suffix = suf;
            }
        });
        console.log(`${prefix}${value<0?'':' '}${value.toFixed(3)} / ${suffix}`);
    }
};

const isotopeNet = (fromUranium, fromLeMox, fromLeUranium, fromHeMox, fromHeUranium) => {
    return (
        uraniumRodConsumption * fromUranium +
        leMoxRodConsumption * fromLeMox +
        leUraniumRodConsumption * fromLeUranium +
        heMoxRodConsumption * fromHeMox +
        heUraniumRodConsumption * fromHeUranium
        ) / 9;
}

console.log('ITEM DEPLETION');
addRod('  Uranium Rod            ', uraniumRodConsumption);
addRod('  LE Mox Rod             ', leMoxRodConsumption);
addRod('  LE Uranium Rod         ', leUraniumRodConsumption);
addRod('  HE Mox Rod             ', heMoxRodConsumption);
addRod('  HE Uranium Rod         ', heUraniumRodConsumption);
addRod('  Control Rod            ', controlRodConsumption);
addRod('  Invar Plate            ', invarPlateConsumption);
addRod('  Carbon Plate           ', carbonPlateConsumption);
console.log('ISOTOPE NET');
addRod('  Uranium 235            ', isotopeNet(1, 0, -3, 0, -9));
addRod('  Uranium 238            ', isotopeNet(53, -24, -24, -18, -18));
addRod('  Plutonium              ', isotopeNet(27, 21, 24, 9, 18));

console.log(map.toString())