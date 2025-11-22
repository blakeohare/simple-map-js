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