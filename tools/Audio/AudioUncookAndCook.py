import os
from UbiArtPY import RAKI

PLATFORM = "PC"
# It detects if it's an amb

os.makedirs("input", exist_ok=True)
os.makedirs("output", exist_ok=True)

for file in os.listdir("input"):
    if os.path.isfile(f"input/{file}"):
        print(f"Converting {file} folder to {PLATFORM=}")
        RAKI.UnCookAndCook(f"input/{file}", f"output/{file}", PLATFORM)


