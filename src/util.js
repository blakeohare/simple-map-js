
const range = n => {
    let arr = [];
    for (let i = 0; i < n; i++) arr.push(null);
    return arr;
};

const makeGrid = (width, height) => {
    return range(width).map(() => range(height).map(() => null));
};
