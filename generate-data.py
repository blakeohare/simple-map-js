import json
import math
import os
import sys

def file_read_text(path):
    c = open(path.replace('/', os.sep), 'rt')
    t = c.read()
    c.close()
    return t.replace('\r\n', '\n')

def file_write_text(path, content):
    c = open(path.replace('/', os.sep), 'wb')
    c.write(content.replace('\r\n', '\n').encode('utf-8'))
    c.close()

def make_grid(width, height):
    cols = []
    cell = [None]
    for i in range(width):
        cols.append(height * cell)
    return cols

def get_countries():
    lines = file_read_text('./raw/country_info.txt').split('\n')
    lines = filter(
        lambda line: line != '' and line[0] != '#',
        lines)
    cols = map(
        lambda line: line.split('\t'),
        lines)
    countries = map(
        lambda cols: { 'id': cols[0], 'name': cols[4], 'refId': int(cols[-3]) },
        cols)

    return countries

def get_shape_data_raw():
    lines = file_read_text('./raw/shapes_all_low.txt').strip().split('\n')
    lines = lines[1:]
    info_by_ref_id = {}
    for line in lines:
        parts = line.split('\t')
        ref_id = int(parts[0].strip())
        info = json.loads(parts[1].strip())
        info_by_ref_id[ref_id] = info
    return info_by_ref_id

POLYGON_BUF_X = []
POLYGON_BUF_Y = []
EPSILON = 0.0000001
def is_point_inside_polygon(x, y, pts):

    # This uses the even-odd scanline method.
    # First we convert all coordinates into integers to simplify the math
    # To convert to integers, multiply the float value by 1 million and floor (int()) it.
    # Then multiply by 2. This guarantees that all geographic coordinate information is
    # even numbers. The input has the same transformation applied to it, but is then
    # incremented by 1 to guarantee that the input is odd. This prevents ambiguous
    # vertical line segments from interfering with the calculation.

    x = 2 * int(x * 1_000_000 + EPSILON) + 1
    y = 2 * int(y * 1_000_000 + EPSILON) + 1
    pt_count = len(pts)
    while len(POLYGON_BUF_X) <= pt_count:
        POLYGON_BUF_X.append(0)
        POLYGON_BUF_Y.append(0)
    for i in range(-1, pt_count):
        pt_x, pt_y = pts[i]
        POLYGON_BUF_X[i + 1] = 2 * int(pt_x * 1_000_000 + EPSILON)
        POLYGON_BUF_Y[i + 1] = 2 * int(pt_y * 1_000_000 + EPSILON)

    # determine how many line segments are cross if you draw a line from the
    # top of the map (x, y = 0) to the point (x, y). Because the input coordinates
    # are odd and the geographic coordinates are even, there will be no vertical
    # line segments encountered. If the number of line segments that are above the
    # y coordinate is odd, then you are inside the polygon shape. If the number
    # of line segments that are cross is even, then you are outside of the shape.

    crossings = 0
    for i in range(pt_count):

        px1 = POLYGON_BUF_X[i]
        px2 = POLYGON_BUF_X[i + 1]
        py1 = POLYGON_BUF_Y[i]
        py2 = POLYGON_BUF_Y[i + 1]
        if y < py1 and y < py2: continue # we're too far north
        if x < px1 and x < px2: continue # we're too far west
        if x > px1 and x > px2: continue # we're too far east

        if y > py1 and y > py2: # we're south, it definitively counts without other math
            crossings += 1
            continue

        # at this point we're ambiguously within the bounding box of the diagnoal.
        dy = py2 - py1 # pt2 rise from pt1
        dx = px2 - px1 # pt2 run from pt1
        m = dy / dx # slope
        ox = x - px1 # input run from pt1
        line_y = m * ox + py1
        if line_y < y:
            crossings += 1

    return crossings % 2 == 1


def gen_cache():
    countries = get_countries()
    shape_lookup = get_shape_data_raw()

    flat_polygons = []
    polygon_by_id = {}
    for country in countries:
        print("Computing geographic information for " + country['name'])

        shape = shape_lookup.get(country['refId'])
        if shape == None:
            print(country['name'] + " has no shape info?")
            continue

        if shape['type'] == 'Polygon':
            raw_geometry_info = [shape['coordinates']]
        elif shape['type'] == 'MultiPolygon':
            raw_geometry_info = shape['coordinates']
        else:
            raise Exception()
        polygon_list = []
        for list_of_point_lists in raw_geometry_info:
            for point_list in list_of_point_lists:
                polygon_list.append(point_list)

        x, y = polygon_list[0][0]
        x, y = polygon_list[-1][0]
        x, y = polygon_list[0][-1]
        x, y = polygon_list[-1][-1]

        for polygon in polygon_list:
            if polygon[0][0] == polygon[-1][0] and polygon[-1][1] == polygon[-1][1]:
                polygon.pop()
            x, y = polygon[0]
            left = x
            right = x
            top = y
            bottom = y
            far_east = False
            far_west = False
            for pt in polygon:
                x, y = pt
                left = min(left, x)
                top = max(top, y)
                right = max(right, x)
                bottom = min(bottom, y)
                far_east = far_east or x > 160
                far_west = far_west or x < -160
            if far_east and far_west:
                print(country['name'] + ' is both far east and west' + '*' * 25)
                print("Skipping!")
                continue
            entry = {
                'polygonId': str(len(flat_polygons)),
                'country': country['id'],
                'points': polygon,
                'boundingBox': [left, top, right, bottom]
            }
            flat_polygons.append(entry)
            polygon_by_id[entry['polygonId']] = entry

    for polygon in flat_polygons:
        normalized = []
        for pt in polygon['points']:
            x = (pt[0] + 180) / 360.0
            y = 1.0 - (pt[1] + 90) / 180.0
            if x < 0 or x > 1 or y < 0 or y > 1: raise Exception()
            normalized.append((x, y))
        polygon['normPts'] = normalized
        x, y = normalized[0]
        normBB = [x, y, x, y]
        for pt in normalized:
            x, y = pt
            normBB[0] = min(x, normBB[0])
            normBB[1] = min(y, normBB[1])
            normBB[2] = max(x, normBB[2])
            normBB[3] = max(y, normBB[3])
        polygon['normBB'] = normBB

    SPITBALL_WIDTH = 400
    SPITBALL_HEIGHT = 200
    spitball_lookup = make_grid(SPITBALL_WIDTH, SPITBALL_HEIGHT)
    for x in range(SPITBALL_WIDTH):
        for y in range(SPITBALL_HEIGHT):
            spitball_lookup[x][y] = []

    for polygon in flat_polygons:
        bb_left, bb_top, bb_right, bb_bottom = polygon['normBB']
        left_col = max(0, int(bb_left * SPITBALL_WIDTH))
        right_col = min(SPITBALL_WIDTH - 1, int(bb_right * SPITBALL_WIDTH + 1))
        top_row = max(0, int(bb_top * SPITBALL_HEIGHT))
        bottom_row = min(SPITBALL_HEIGHT - 1, int(bb_bottom * SPITBALL_HEIGHT + 1))
        for x in range(left_col, right_col + 1):
            for y in range(top_row, bottom_row + 1):
                spitball_lookup[x][y].append(polygon)
    spitball_cache[0] = spitball_lookup

def coord_to_ratio(lat, lon):
    return ((lon + 180) / 360.0, 1 - (lat + 90) / 180.0)

UK_REGIONS = [
    {
        'country': 'UK:NI',
        'base': ['RECT', coord_to_ratio(55.346849, -8.324762), coord_to_ratio(53.976932, -5.326929)],
        'exclusions': [
            ['RECT', coord_to_ratio(55.615832, -6.004568), coord_to_ratio(55.137619, -4.748092)]
        ],
    },
    {
        'country': 'UK:WA',
        'base': ['RECT', coord_to_ratio(53.679425, -5.646503), coord_to_ratio(51.363963, -3.021229)],
    },
    {
        'country': 'UK:SC',
        'base': ['ABOVE', coord_to_ratio(54.997964, -3.126487), coord_to_ratio(55.820819, -1.931281)]
    },
    {
        'country': 'UK:EN',
        'base': ['RECT', coord_to_ratio(56.362919, -10.020512), coord_to_ratio(49, 5.692914)]
    }
]

def check_if_point_in_geometry(x, y, geo):
    if geo[0] == 'RECT':
        xs = [geo[1][0], geo[2][0]]
        ys = [geo[1][1], geo[2][1]]
        if xs[0] > xs[1]: xs.reverse()
        if not (xs[0] < x < xs[1]): return False
        if ys[0] > ys[1]: ys.reverse()
        return ys[0] < y < ys[1]

    if geo[0] == 'ABOVE' or geo[0] == 'BELOW':
        x1, y1 = geo[1]
        x2, y2 = geo[2]
        x_progress =  (x - x1) / (x2 - x1)
        y_rise_per_interval = (y2 - y1)
        line_y = x_progress * y_rise_per_interval + y1
        is_above = y < line_y
        if geo[0] == 'ABOVE': return is_above
        return not is_above

    raise Exception()

def get_specific_region(x, y, lookup, default_country):

    for test in lookup:
        if check_if_point_in_geometry(x, y, test['base']):
            is_match = True
            for counter_test in test.get('exclusions', ''):
                if check_if_point_in_geometry(x, y, counter_test):
                    is_match = False
                    break
            if is_match:
                return test['country']

    return default_country

def get_uk_country(x, y):
    return get_specific_region(x, y, UK_REGIONS, 'UK:?')

spitball_cache = [None]

def generate_country_grid(lon_west, lat_north, lon_east, lat_south, pixel_width, pixel_height, progress_logger = None):

    if spitball_cache[0] == None:
        gen_cache()
    spitball_lookup = spitball_cache[0]
    SPITBALL_WIDTH = len(spitball_lookup)
    SPITBALL_HEIGHT = len(spitball_lookup[0])

    NORM_LEFT = (lon_west + 180) / 360.0
    NORM_RIGHT = (lon_east + 180) / 360.0
    NORM_TOP = 1 - (lat_north + 90) / 180.0
    NORM_BOTTOM = 1 - (lat_south + 90) / 180.0

    NORM_WIDTH = NORM_RIGHT - NORM_LEFT
    NORM_HEIGHT = NORM_BOTTOM - NORM_TOP

    PIXEL_WIDTH = pixel_width
    PIXEL_HEIGHT = pixel_height

    grid = make_grid(PIXEL_WIDTH, PIXEL_HEIGHT)

    for y in range(PIXEL_HEIGHT):
        if progress_logger != None: progress_logger(y / PIXEL_HEIGHT)
        y_progress = y / PIXEL_HEIGHT
        pt_y = y_progress * NORM_HEIGHT + NORM_TOP
        for x in range(PIXEL_WIDTH):
            x_progress = x / PIXEL_WIDTH
            pt_x = x_progress * NORM_WIDTH + NORM_LEFT
            sb_col = int(SPITBALL_WIDTH * pt_x)
            sb_row = int(SPITBALL_HEIGHT * pt_y)
            polygons = spitball_lookup[sb_col][sb_row]
            country = None
            for pg in polygons:
                if is_point_inside_polygon(pt_x, pt_y, pg['normPts']):
                    country = pg['country']
                    if country == 'GB':
                        country = get_uk_country(pt_x, pt_y)
                    break
            grid[x][y] = country

    return grid

def load_configuration(name):
    locations = json.loads(file_read_text('./configured-locations.json'))['locations']
    for loc in locations:
        if loc['name'] == name:
            return loc
    return None

def main(args):

    if len(args) != 2:
        print('\n'.join([
            "Usage:",
            "python generate-data.py location-id resolution",
            "",
            "location-id must be a name parameter in configured-locations.json",
            "resolution must be one of HIGH | MED | LOW (corresponding to 400, 800, 1200 pixel width)",
            ""
        ]))
        return

    name = args[0]

    configuration = load_configuration(args[0])
    if configuration == None:
        print("Configuration not found in configured-locations.json (case sensitive): '" + args[0] + "'")
        return

    resolutions = ('HIGH', 'MED', 'LOW')
    resolution = args[1].upper()
    if resolution not in resolutions:
        print("Resolution must be one of " + ', '.join(resolutions))
        return

    pixel_width = {
        'HIGH': 1200,
        'MED': 800,
        'LOW': 400,
    }.get(resolution.upper())

    pixel_height = pixel_width * 2

    # TODO: remove this!
    # pixel_width = int(pixel_width / 5)
    # pixel_height = int(pixel_height / 5)

    west = configuration['nw'][1]
    north = configuration['nw'][0]
    east = configuration['se'][1]
    south = configuration['se'][0]



    print("Generating rasterized grid from vector data")
    grid = generate_country_grid(
        west, north, east, south,
        pixel_width, pixel_height,
        lambda ratio: print("Progress: " + str(int(ratio * 100 + 0.5)) + '%')
    )

    print("Converting rasterization to vertical strip format...")
    strip_data = [hex(pixel_width)[2:], hex(pixel_height)[2:]]
    for x in range(pixel_width):
        strips = []
        current_strip = None
        for y in range(pixel_height):
            country = grid[x][y]
            is_ocean = country == None
            is_same = current_strip == None if is_ocean else (current_strip != None and current_strip[0] == country)
            if is_same:
                if not is_ocean:
                    current_strip[2] = y
            else:
                if is_ocean:
                    current_strip = None
                else:
                    current_strip = [country, y, y]
                    strips.append(current_strip)

        strip_flat = []
        for strip in strips:
            strip_flat.append(strip[0] + ',' + hex(strip[1])[2:] + ',' + hex(strip[2])[2:])
        strip_data.append(','.join(strip_flat))
    all_data = '|'.join(strip_data)

    print("Saving to pre-gen JavaScript file...")
    path = './pre-gen/simplemap-' + name + '-' + resolution.lower() + '.js'
    js_code = ''.join([
        "SimpleMap.loadData('",
        name,
        "',\n'",
        all_data,
        "');\n"
    ])
    file_write_text(path, js_code)

    print("Done. Data saved to " + path)

if __name__ == '__main__':
    main(sys.argv[1:])
