const createDemoPage = () => {
    let mapLabelsById = {
        'australia-new-zealand': "Australia/NZ",
        'europe': "Europe",
        'hawaii': "Hawaii",
        'iceland': "Iceland",
        'japan': "Japan",
    };

    const oceanColor = 'rgb(85, 168, 240)';
    const landColorRgb = [30, 126, 30];
    const landColorLightnessVarianceSize = 0.5;
    const pixelWidth = 800;
    const pixelHeight = 600;

    // Gets a color similar to landColorRgb but with a randomly chosen ratio applied
    // to each RGB component to make it lighter or darker.
    let getVariedLandColor = () => {
        let ratio = Math.random() * landColorLightnessVarianceSize + 1 - landColorLightnessVarianceSize / 2;
        return 'rgb(' + landColorRgb.map(value => {
            let newColor = Math.floor(value * ratio);
            let clamped = Math.max(0, Math.min(255, newColor));
            return clamped;
        }).join(', ') + ')';
    };

    let mapInstance = SimpleMap.create(pixelWidth, pixelHeight);
    let mapHost = document.getElementById('map-host');
    mapHost.append(mapInstance.getDomElement());

    let mapPicker = document.getElementById('map-picker');

    Object.keys(mapLabelsById).forEach(mapId => {
        let mapLabel = mapLabelsById[mapId];
        let button = document.createElement('button');
        button.innerText = mapLabel;
        button.addEventListener('click', () => {
            mapInstance.clearBackground(oceanColor);
            mapInstance.setActiveView(mapId);
            mapInstance.getAllRegions().forEach(regionId => {
                mapInstance.setRegionColor(regionId, getVariedLandColor());
            });
        });
        mapPicker.append(button);
    });
};
