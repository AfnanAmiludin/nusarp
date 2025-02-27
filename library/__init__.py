import os
import sys
from pathlib import Path

cwd = Path(__file__).resolve().parent
# python library here :
sys.path.append(os.path.abspath(os.path.join(cwd)))
sys.path.append(os.path.abspath(os.path.join(cwd, 'channelsredis')))
sys.path.append(os.path.abspath(os.path.join(cwd, 'dotnet')))
sys.path.append(os.path.abspath(os.path.join(cwd, 'captcha')))
sys.path.append(os.path.abspath(os.path.join(cwd, 'timeago')))
sys.path.append(os.path.abspath(os.path.join(cwd, 'renderblock')))
sys.path.append(os.path.abspath(os.path.join(cwd, 'cacheops')))
sys.path.append(os.path.abspath(os.path.join(cwd, 'yamlconfig')))
sys.path.append(os.path.abspath(os.path.join(cwd, 'currentuser')))
sys.path.append(os.path.abspath(os.path.join(cwd, 'simplehistory')))
sys.path.append(os.path.abspath(os.path.join(cwd, 'modelutils')))
sys.path.append(os.path.abspath(os.path.join(cwd, 'organizations')))
sys.path.append(os.path.abspath(os.path.join(cwd, 'extensions')))
sys.path.append(os.path.abspath(os.path.join(cwd, 'corsheaders')))
sys.path.append(os.path.abspath(os.path.join(cwd, 'djangoredis')))
sys.path.append(os.path.abspath(os.path.join(cwd, 'treebeard')))
sys.path.append(os.path.abspath(os.path.join(cwd, 'restframeworkflexfields')))
sys.path.append(os.path.abspath(os.path.join(cwd, 'jsreverse')))
sys.path.append(os.path.abspath(os.path.join(cwd, 'revproxy')))
sys.path.append(os.path.abspath(os.path.join(cwd, 'hueymonitor')))
sys.path.append(os.path.abspath(os.path.join(cwd, 'hueymonitorutils')))
sys.path.append(os.path.abspath(os.path.join(cwd, 'pyodbc')))
sys.path.append(os.path.abspath(os.path.join(cwd, 'vobject')))
sys.path.append(os.path.abspath(os.path.join(cwd, 'privatestorage')))
sys.path.append(os.path.abspath(os.path.join(cwd, 'hijack')))
sys.path.append(os.path.abspath(os.path.join(cwd, 'postgres')))
# add sys.path to environment
os.environ['PATH'] += os.pathsep + os.pathsep.join(sys.path)
