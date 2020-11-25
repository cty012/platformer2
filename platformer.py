import os
import sys

import main.app as app
from utils import args as a, settings


# Prepare save_path
save_path = os.path.join(os.path.expanduser('~'), '.PRISMSDeveloperSociety', 'platformer2')
_save_path_requires_subpaths = ['log']
for sprs in _save_path_requires_subpaths:
    try:
        os.makedirs(os.path.join(save_path, sprs))
    except FileExistsError:
        pass

# Prepare path
if getattr(sys, 'frozen', False):
    import time
    t = time.time_ns()

    path = sys._MEIPASS

    sys.stdout = open(os.path.join(save_path, 'log', f'{t}.log'), 'w')
    sys.stderr = sys.stdout

else:
    path = os.path.dirname(__file__)


# Create args
args = a.Args(scale=1, path=path, save_path=save_path)


# Load settings
settings.default_try_get_delim = '.'
settings.load(
    path=os.path.join(save_path, 'settings.json'),
    default_path=os.path.join(path, 'src', 'default_settings.json')
)

app.launch(args)
