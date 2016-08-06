import subprocess

try:
    subprocess.check_call(['pip install -r requirement.txt'], shell=True)
except Exception:
    pass
try:
    subprocess.check_call(['~/.nvm/versions/node/v5.6.0/bin/npm install'], shell=True)
except Exception:
    pass
try:
    subprocess.check_call(['~/.nvm/versions/node/v5.6.0/bin/bower install'], shell=True)
except Exception:
    pass

# subprocess.check_call(['python run.py'], shell=True)
# subprocess.call(['nvm use v5.5.6'], shell=True)
