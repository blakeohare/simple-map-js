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

