"""Test setup script to verify installation of required data science packages.

This script checks that Python and essential data science libraries (pandas, numpy, requests)
are properly installed and accessible by printing their version information.
"""
import sys

import pandas as pd
import numpy as np
import requests

print("✓ Python version:", sys.version)
print("✓ Pandas version:", pd.__version__)
print("✓ NumPy version:", np.__version__)
print("✓ Requests version:", requests.__version__)
print("\n✓✓✓ Setup successful! ✓✓✓")