import os
import sys
from pathlib import Path

cwd = Path(__file__).resolve().parent
# python library here :
sys.path.append(os.path.abspath(os.path.join(cwd)))
sys.path.append(os.path.abspath(os.path.join(cwd, 'pghistory')))
sys.path.append(os.path.abspath(os.path.join(cwd, 'pgtrigger')))
# add sys.path to environment
os.environ['PATH'] += os.pathsep + os.pathsep.join(sys.path)
