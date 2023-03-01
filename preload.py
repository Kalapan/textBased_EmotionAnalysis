

import sys

# Remove the numpy module from sys.modules
if 'numpy' in sys.modules:
    del sys.modules['transformers', 'pandas', 'pymongo', 'snscrape.modules.twitter']