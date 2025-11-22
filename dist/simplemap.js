const SimpleMap = (() => {

const range = n => {
    let arr = [];
    for (let i = 0; i < n; i++) arr.push(null);
    return arr;
};

const makeGrid = (width, height) => {
    return range(width).map(() => range(height).map(() => null));
};

const DataLoader = (() => {

    let dataStore = {};
    let activeView = null;

    let loadData = (name, rawValue) => {
        dataStore[name] = parseData(rawValue);
    };

    let setActiveView = view => {
        let data = dataStore[view];
        if (!data) throw new Error("There is no loaded data for " + activeView);
        activeView = view;
    };

    let parseData = rawValue => {
        let cols = rawValue.split('|');
        let parseHex = s => parseInt(s, 16);
        let width = parseHex(cols[0]);
        let height = parseHex(cols[1]);
        let colsOut = [];
        for (let x = 0; x < width; x++) {
            let col = cols[x + 2];
            let cells = col.split(',');
            let colData = [];
            let cellCount = cells.length;
            if (cellCount > 1) {
                for (let y = 0; y < cellCount; y += 3) {
                    let country = cells[y];
                    let yStart = parseInt(cells[y + 1], 16);
                    let yEnd = parseInt(cells[y + 2], 16) + 1;
                    colData.push({ country, yStart, yEnd });
                }
            }
            colsOut.push(colData);
        }
        return { width, height, grid: colsOut };
    };

    let getData = () => dataStore[activeView];

    loadData('none', '1|1||');
    setActiveView('none');

    return {
        getData,
        setActiveView,
        loadData,
    };
})();
const createCanvasMap = () => {

    let canvas = document.createElement('canvas');
    let ctx = null;
    let setRasterSize = (pixelWidth, pixelHeight) => {
        canvas.width = pixelWidth;
        canvas.height = pixelHeight;
        ctx = canvas.getContext('2d');
    };

    let allCountries = {};

    let refreshData = () => {

        let data = DataLoader.getData();;
        let dataWidth = data.width;
        let dataHeight = data.height;
        let rawDataLookup = data.grid;

        allCountries = {};

        let { width, height } = canvas;
        for (let x = 0; x < width; x++) {
            let colNum = Math.floor(dataWidth * x / width);
            let strips = rawDataLookup[colNum];
            if (!Array.isArray(strips)) debugger;
            for (let strip of strips) {
                let { country, yStart, yEnd } = strip;
                let node = allCountries[country];
                if (!node) {
                    node = { id: country, strips: [] };
                    allCountries[country] = node;
                }
                node.strips.push([
                    x,
                    Math.floor(height * yStart / dataHeight),
                    Math.floor(height * yEnd / dataHeight),
                ]);
            }
        }

    };

    let clearBackground = color => {
        ctx.fillStyle = color;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    };

    let setCountryColor = (id, color) => {
        country = allCountries[id];
        if (!country) return;
        ctx.fillStyle = color;
        for (let strip of country.strips) {
            ctx.fillRect(strip[0], strip[1], 1, strip[2] - strip[1]);
        }
    };

    return {
        setRasterSize,
        refreshData,
        clearBackground,
        setCountryColor,
        getAllCountries: () => Object.keys(allCountries).sort(),
        getCanvasElement: () => canvas,
    };
};

let create = (width, height) => {
    let instance = createCanvasMap();
    instance.setRasterSize(width, height);
    let o = Object.freeze({
        setRasterSize: (w, h) => { instance.setRasterSize(w, h); return o; },
        clearBackground: cssColor => { instance.clearBackground(cssColor); return o; },
        setRegionColor: (regionId, cssColor) => { instance.setCountryColor(regionId, cssColor); return o; },
        getAllRegions: () => instance.getAllCountries(),
        getDomElement: () => instance.getCanvasElement(),
        setActiveView: mapId => { 
            DataLoader.setActiveView(mapId); 
            instance.refreshData();
            return o; 
        },
    });
    return o;
};

let loadData = (mapId, rawData) => DataLoader.loadData(mapId, rawData);


return Object.freeze({ loadData, create });
})();
