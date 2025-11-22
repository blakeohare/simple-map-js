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
