import sys

if sys.version >= '3':
    from .pyparsing2 import *
    print("pyparsing 2.0.0")
else:
    from .pyparsing import *
    print("pyparsing 1.5.7")