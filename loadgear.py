import gears
import re

# Cache the contents of the gears module, for later use.
GEARS_DIR = dir( gears )

def load( g_file ):
    """Given an open file, load the text and return the list of described gears"""
    # If it is a command, do that command.
    # If it has an =, add it to the dict
    # Otherwise, check to see if it's a Gear type

    list_of_gears = []
    current_gear = None
    gear_class = None
    current_dict = {}

    for rawline in g_file:
        line = rawline.strip()
        if len( line ) > 0:
            if "=" in line:
                # This is a dict line. Add to the current_dict.
                m = re.match(r"(\w+)=(\w+)", line )

            elif line in GEARS_DIR:
                # This is a gear request.
                gear_class = getattr( gears , line )


