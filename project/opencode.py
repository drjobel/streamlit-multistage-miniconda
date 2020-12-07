# Auxiliary to load the opencode package

import os
import sys
# Ensuring to add the opencode to the path
opencode_path = os.path.abspath('./opencode')

if opencode_path not in sys.path:
    sys.path.append(opencode_path)
