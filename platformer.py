import os
import sys

import main.app as app
import utils.args as a


if getattr(sys, 'frozen', False):
    import time
    t = time.time_ns()

    path = sys._MEIPASS
    save_path = os.path.join(os.path.expanduser('~'), '.PRISMSDeveloperSociety', 'platformer2')
    try:
        os.makedirs(os.path.join(save_path, 'log'))
    except FileExistsError:
        pass

    sys.stdout = open(os.path.join(save_path, 'log', f'{t}.log'), 'w')
    sys.stderr = sys.stdout

else:
    path = os.path.dirname(__file__)

args = a.Args(scale=1, path=path)
app.launch(args)
