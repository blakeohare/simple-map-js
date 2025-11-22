# SimpleMap.js

A canvas-based drop-in vanilla JavaScript library to render countries as solid colors.

> Note: Currently this is a tinker project I made for myself but decided to release
> as open source as it seemed somewhat useful. As such the configurability is a bit
> low and heavy-handed (requires running a python commands) and the pre-processing
> is a bit slow.

## Usage

Copy `simplemap.js` or `simplemap.min.js` to your project along with the
corresponding `pre-gen/` files you wish to display. The geographic data from
`pre-gen` must be loaded AFTER `simplemap.js`. Feel free to concatenate these
files together to ensure this is the case.

As an example, you can display a 400x300 map of europe with random country colors
using the following code:

```javascript
let myMap = SimpleMap.create(400, 300); // sample width and height
myMap.setActiveView('europe');
myMap.clearBackground('#5ba5ef');
for (let regionId of myMap.getAllRegions()) {
    let randomCssColor =
        'rgb(' + [0, 0, 0].map(() => Math.floor(Math.random() * 255)).join(',') + ')';
    myMap.setRegionColor(regionId, randomCssColor);
}
document.body.append(myMap.getDomElement());
```

The view and rasterization size of the map instance can be reset at any
time using `.setActiveView(mapName)` and `.setRasterSize(width, height)`.

Note that `.clearBackground(cssColor)` resets the full canvas and regions will
not be drawn until you specifically ask it to do so. This allows you to render
specific countries.

## Generating geographic data

There are a handful of pre-generated maps in `pre-gen`. You can create more using
the `generate-data.py` script and the `configured-locations.json` files.

The `pre-gen` files encode a rectangular region and the map will only display the information
within that region regardless of aspect ratio of the canvas. This is a known bug.

First add your region to the JSON file following the format of the existing regions:
```json
{
    "locations": [
        ...
        {
            "name": "my-region-name",
            "nw": [latitude, longitutde], // northwest corner
            "se": [latitude, longitude] // southeast corner
        },
        ...
    ]
}
```

Once added, run the python script `generate-data.py` with the name of the region
you provided in the file followed by `HIGH`, `MED`, or `LOW` to specify the
resolution size.

Once finished, the file will appear in `pre-gen/simplemap-{name}-{high|med|low}.js`.

Including this file in your codebase will load it with the map ID of the name provided.

```javascript
myMapInstance.setActiveView('my-region-name');
mymapInstance.clearBackground(...);
myMapInstance.setRegionColor(...); // etc.
```

## Data Source

The country information and borders are provided by
[GeoNames](https://www.geonames.org/about.html) via the
[Creative Commons Attribute 4.0 License](https://creativecommons.org/licenses/by/4.0/).

## Known Issues

- You are unable to create rectangular regions that span the international date
  line.
- Tiny countries are nearly-guaranteed invisible. Eventually I'd like to make a
  "clickable dot" mode.
- **United Kingdom** - This is subdivided into separate regions. I did this manually to
  provide a distinction for the original project I made this for at very low
  resolutions. This looks terrible at high resolution as the borders between
  England/Wales/Scotland are straight lines.
- **Antarctica** - it is missing.
- **Maldives** - the vector data surrounds actual land. Because these are tiny
  atolls, the sampling algorithm will almost always miss and ultimately not
  render it.

## Feature TODO list

- Ability to provide/configure 2nd-level administrative division
  (state/province/etc).
- Performance improvements to the generator script (currently the polygon
  scanlines search through all line segments instead of just the ones in the
  current scanline)
- Ability to render border line
- Cropping the view to ensure realistic aspect ratio.
- More pre-gens in general.
