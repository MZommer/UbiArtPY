import os
from UbiArtPY import RAKI

PLATFORM = "NX"
IS_AMB = False

os.makedirs("input", exist_ok=True)
os.makedirs("output", exist_ok=True)

for file in os.listdir("input"):
    if os.path.isfile(f"input/{file}"):
        print(f"Converting {file} folder to {PLATFORM=} {IS_AMB=}")
        audio = RAKI()
        audio.Cook(f"input/{file}", f"output/{file}.ckd", PLATFORM, isAMB=IS_AMB)
        print("Converted successfully!")
