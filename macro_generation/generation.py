import gdstk
import random
import math
min_metal6_width = 1.7 #1.64  # Minimum Metal6 width in microns
min_metal6_spacing = 1.7 #1.64 


total_width = 104
total_height = 68
cell_bounds = (0, 0, total_width, total_height)

length = 4  # Reduced from 8




# The GDSII file is called a library, which contains multiple cells.
lib = gdstk.Library()

# Geometry must be placed in cells.
cell = lib.new_cell("my_logo")


def generate_seed_points(width, height, count, margin, jitter=0.3):
    cols = math.ceil(math.sqrt(count))
    rows = math.ceil(count / cols)
    cell_w = width / cols
    cell_h = height / rows
    seeds = []
    for r in range(rows):
        for c in range(cols):
            if len(seeds) >= count:
                break
            base_x = (c + 0.5) * cell_w
            base_y = (r + 0.5) * cell_h
            x = base_x + random.uniform(-jitter, jitter) * cell_w
            y = base_y + random.uniform(-jitter, jitter) * cell_h
            x = max(margin, min(width - margin, x))
            y = max(margin, min(height - margin, y))
            seeds.append((x, y))
    return seeds


def build_axis_steps(length, preferred, minimum):
    steps = [0.0]
    position = 0.0
    while length - position > minimum:
        candidate = position + preferred
        if candidate >= length:
            steps.append(length)
            break
        if length - candidate < minimum:
            steps.append(length)
            break
        steps.append(candidate)
        position = candidate
    if steps[-1] != length:
        steps.append(length)
    return steps


def create_voronoi_regions(width, height, min_feature):
    target_seed_count = random.randint(6, 9)
    seeds = generate_seed_points(width, height, target_seed_count, min_feature)
    tile_size = max(min_feature, min_metal6_spacing) * 2.0
    x_edges = build_axis_steps(width, tile_size, min_feature)
    y_edges = build_axis_steps(height, tile_size, min_feature)

    x_tiles = len(x_edges) - 1
    y_tiles = len(y_edges) - 1
    assignments = [[None for _ in range(y_tiles)] for _ in range(x_tiles)]
    for xi in range(len(x_edges) - 1):
        for yi in range(len(y_edges) - 1):
            x0, x1 = x_edges[xi], x_edges[xi + 1]
            y0, y1 = y_edges[yi], y_edges[yi + 1]
            cx = (x0 + x1) * 0.5
            cy = (y0 + y1) * 0.5
            nearest = min(
                range(len(seeds)),
                key=lambda idx: (seeds[idx][0] - cx) ** 2 + (seeds[idx][1] - cy) ** 2,
            )
            assignments[xi][yi] = nearest

    line_width = max(min_feature * 1.6, min_feature + 0.5)
    half_line = line_width / 2.0
    borders = []

    # Vertical borders
    for xi in range(1, x_tiles):
        x = x_edges[xi]
        for yi in range(y_tiles):
            left = assignments[xi - 1][yi]
            right = assignments[xi][yi]
            if left != right:
                y0 = y_edges[yi]
                y1 = y_edges[yi + 1]
                borders.append(
                    gdstk.rectangle(
                        (max(0.0, x - half_line), y0),
                        (min(width, x + half_line), y1),
                        layer=71,
                        datatype=20,
                    )
                )

    # Horizontal borders
    for yi in range(1, y_tiles):
        y = y_edges[yi]
        for xi in range(x_tiles):
            bottom = assignments[xi][yi - 1]
            top = assignments[xi][yi]
            if bottom != top:
                x0 = x_edges[xi]
                x1 = x_edges[xi + 1]
                borders.append(
                    gdstk.rectangle(
                        (x0, max(0.0, y - half_line)),
                        (x1, min(height, y + half_line)),
                        layer=71,
                        datatype=20,
                    )
                )

    merged = gdstk.boolean(borders, [], "or", layer=71, datatype=20)
    return merged if merged else []


voronoi_regions = create_voronoi_regions(total_width, total_height, min_metal6_width)
for region in voronoi_regions:
    cell.add(region)
        

pr_boundary = gdstk.rectangle((0, 0), (length,length), layer=235, datatype=4)
cell.add(pr_boundary)



# Generate LEF file
def write_lef_file(filename, cell_name, cell_bounds, pins):
    """Write a LEF file for the cell"""
    with open(filename, 'w') as f:
        f.write("# LEF file generated for {}\n".format(cell_name))
        f.write("VERSION 5.8 ;\n")
        f.write("NAMESCASESENSITIVE ON ;\n")
        f.write("DIVIDERCHAR \"/\" ;\n")
        f.write("BUSBITCHARS \"[]\" ;\n")
        f.write("UNITS\n")
        f.write("   DATABASE MICRONS 1000 ;\n")
        f.write("END UNITS\n\n")
        
        # Define the cell
        f.write("MACRO {}\n".format(cell_name))
        f.write("   CLASS BLOCK ;\n")
        f.write("   FOREIGN {} 0 0 ;\n".format(cell_name))
        f.write("   SIZE {:.3f} BY {:.3f} ;\n".format(cell_bounds[2] - cell_bounds[0], cell_bounds[3] - cell_bounds[1]))
        f.write("   SYMMETRY X Y ;\n")
        
        # No pins - pure blackbox module
        # No OBS section - keep LEF simple
        
        f.write("END {}\n".format(cell_name))

# Calculate cell bounds for 3x2 grid layout


# Write LEF file
write_lef_file("../macros/my_logo.lef", "my_logo", cell_bounds, [])

# Save the library in a GDSII or OASIS file.
lib.write_gds("../macros/my_logo.gds")

# Optionally, save an image of the cell as SVG.
cell.write_svg("../macros/my_logo.svg")