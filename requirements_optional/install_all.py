# install all txt requirements in current folder
import os
os.chdir(os.path.dirname(__file__))
for i in os.listdir():
    if i.endswith(".txt"):
        os.system("pip install -r " + i)
