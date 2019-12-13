# Creates the DJANGO SECRET_KEY and adds it to the .env file or creates the .env file

import os, random, json
from collections import OrderedDict

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(THIS_DIR,'.env')
SECRET_KEY = ''.join([random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])

env = {'SECRET_KEY':SECRET_KEY}

if os.path.isfile(ENV_FILE):
    with open(ENV_FILE,'r') as fid:
        # load while maintaining order
        try:
            old_env = json.load(fid, object_pairs_hook=OrderedDict)
            if 'SECRET_KEY' in old_env:
                raise Exception('Aborted. Already found "SECRET_KEY" in "%s".'%ENV_FILE)
            env.update()
        except ValueError:
            if os.path.getsize(ENV_FILE) != 0: # Only error if not empty
                raise

# (Re)write file
with open(ENV_FILE,'w') as fid:
    json.dump(env,fid,indent=4)