import re
import os

with open("settings.py", 'r') as f1, open("settings.py.1", 'w') as f2:
    for line in f1:
        # print("line:", line)
        f2.write(re.sub("(?<='cookie':\")\S+(?=\",)", "'123123'", line))
# os.remove("settings.py")
# os.rename("settings.py.1", "settings.py")