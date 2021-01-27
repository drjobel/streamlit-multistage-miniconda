# Useful to keep the context of the widgets status or 
# parameters to keep while running the app
# We initialize it here so the values will persist 
# when loaded first from the main `app.py`

# from turpy import Metadata
from inshelve import shelf_read

# context = Metadata({})
# metadata = context.metadata

# metadata = shelf_read('metadata')

# Populate
if metadata is None:
    metadata = {}
