import traceback
import sys
import os
try:
    import importlib
    # ensure repo root is on sys.path when running from scripts/ folder
    repo_root = os.getcwd()
    sys.path.insert(0, repo_root)
    print('sys.path[0:5]=', sys.path[0:5])
    importlib.import_module('flask_app')
    print('imported flask_app successfully')
except Exception:
    traceback.print_exc()
    sys.exit(1)
