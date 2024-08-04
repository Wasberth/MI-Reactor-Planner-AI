const randIntFromDouble = (value) => {
    return Math.floor(value) + (Math.random() < (value % 1) ? 1 : 0);
}

const assert = (cond, msg) => {
    if (!cond) {
        throw Error(msg);
    }
}

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

module.exports = {randIntFromDouble, assert, format}