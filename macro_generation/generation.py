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


right_overlay_points = [
    (5, 15),
    (12, 15),
    (12, 25),
    (10, 25),
    (10, 35),
    (15, 35),
    (15, 55),
    (6, 55),
    (6, 45),
    (8, 45),
    (8, 30),
    (5, 30),
]
right_overlay = gdstk.Polygon(right_overlay_points, layer=71, datatype=20)
cell.add(right_overlay)
        

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