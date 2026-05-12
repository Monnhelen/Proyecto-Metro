"""
Simplify basemap_data.js:
- Round coordinates from 15 decimals → 4 decimals (~11m precision, invisible at city scale)
- Apply Douglas-Peucker simplification to reduce vertex count
- Remove degenerate polygons (< 4 unique points after simplification)
Typical result: 68 MB → 5-10 MB
"""
import json, re, math, sys

TOLERANCE = 0.0002   # ~22m — increase to 0.0005 for even smaller file
PRECISION = 4        # decimal places for coordinates

def rdp(points, eps):
    """Ramer-Douglas-Peucker simplification."""
    if len(points) < 3:
        return points
    # Find the point with the maximum distance
    start, end = points[0], points[-1]
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    dist_sq_line = dx*dx + dy*dy
    max_dist = 0.0
    max_idx = 0
    for i in range(1, len(points) - 1):
        if dist_sq_line == 0:
            d = math.hypot(points[i][0]-start[0], points[i][1]-start[1])
        else:
            t = ((points[i][0]-start[0])*dx + (points[i][1]-start[1])*dy) / dist_sq_line
            t = max(0.0, min(1.0, t))
            proj = (start[0]+t*dx, start[1]+t*dy)
            d = math.hypot(points[i][0]-proj[0], points[i][1]-proj[1])
        if d > max_dist:
            max_dist = d
            max_idx = i
    if max_dist > eps:
        left  = rdp(points[:max_idx+1], eps)
        right = rdp(points[max_idx:], eps)
        return left[:-1] + right
    else:
        return [start, end]

def simplify_ring(ring, eps, prec):
    simplified = rdp(ring, eps)
    rounded = [[round(p[0], prec), round(p[1], prec)] for p in simplified]
    # close the ring
    if rounded and rounded[0] != rounded[-1]:
        rounded.append(rounded[0])
    # need at least 4 points for a valid polygon ring
    return rounded if len(rounded) >= 4 else None

def simplify_geometry(geom, eps, prec):
    t = geom['type']
    if t == 'Polygon':
        new_coords = []
        for ring in geom['coordinates']:
            r = simplify_ring(ring, eps, prec)
            if r:
                new_coords.append(r)
        if not new_coords:
            return None
        return {'type': 'Polygon', 'coordinates': new_coords}
    elif t == 'MultiPolygon':
        new_polys = []
        for poly in geom['coordinates']:
            new_rings = []
            for ring in poly:
                r = simplify_ring(ring, eps, prec)
                if r:
                    new_rings.append(r)
            if new_rings:
                new_polys.append(new_rings)
        if not new_polys:
            return None
        return {'type': 'MultiPolygon', 'coordinates': new_polys}
    else:
        return geom

def process(src_path, dst_path):
    print(f"Reading {src_path} ...")
    with open(src_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract BASEMAP_MANZANAS JSON (ends at the semicolon before BASEMAP_MUN15)
    m = re.search(r'const BASEMAP_MANZANAS\s*=\s*', content)
    m2 = re.search(r'const BASEMAP_MUN15\s*=\s*', content)
    if not m:
        print("ERROR: BASEMAP_MANZANAS not found")
        sys.exit(1)

    json_start = m.end()
    # Find the semicolon that terminates the BASEMAP_MANZANAS statement
    json_end = content.index(';', json_start)
    json_str = content[json_start:json_end]

    # Keep everything after that semicolon (MUN15 + anything else)
    rest_block = content[json_end+1:].lstrip('\n')

    print("Parsing JSON ...")
    data = json.loads(json_str)

    original_count = len(data['features'])
    print(f"Features: {original_count}")

    print(f"Simplifying (tolerance={TOLERANCE}, precision={PRECISION}) ...")
    new_features = []
    for feat in data['features']:
        new_geom = simplify_geometry(feat['geometry'], TOLERANCE, PRECISION)
        if new_geom:
            new_features.append({'type': 'Feature', 'geometry': new_geom, 'properties': feat.get('properties', {})})

    kept = len(new_features)
    print(f"Kept {kept}/{original_count} features ({100*kept//original_count}%)")

    data['features'] = new_features

    print("Serializing ...")
    # Compact JSON — no spaces
    compact = json.dumps(data, separators=(',', ':'), ensure_ascii=False)

    output = f'// ═══════ BASEMAP DATA - MANZANAS (CDMX) ═══════\nconst BASEMAP_MANZANAS={compact};\n{rest_block}'

    with open(dst_path, 'w', encoding='utf-8') as f:
        f.write(output)

    import os
    src_mb = os.path.getsize(src_path) / 1e6
    dst_mb = os.path.getsize(dst_path) / 1e6
    print(f"\nDone: {src_mb:.1f} MB → {dst_mb:.1f} MB  ({100*(1-dst_mb/src_mb):.0f}% reduction)")
    print(f"Output: {dst_path}")

if __name__ == '__main__':
    src = r'c:\Users\ogald\OneDrive\Escritorio\MetroMonica\Proyecto-Metro\basemap_data.js'
    dst = r'c:\Users\ogald\OneDrive\Escritorio\MetroMonica\Proyecto-Metro\basemap_data_simple.js'
    process(src, dst)
