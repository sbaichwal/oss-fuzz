import numpy as np
import os

OSS_FUZZ_DIR = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

source_file = os.path.join(OSS_FUZZ_DIR, "tools/scripts/wolfi-packages.txt")
target_folder = os.path.join(OSS_FUZZ_DIR, "projects/")

output_integrated = os.path.join(OSS_FUZZ_DIR, "tools/scripts/integrated-packages.txt")
output_not_integrated = os.path.join(OSS_FUZZ_DIR, "tools/scripts/not-integrated-packages.txt")

with open(source_file, "r") as f:
    packages = f.read().splitlines()

existing_packages = sorted(os.listdir(target_folder))

source_index = 0
target_index = 0

integrated = []
not_integrated = []

while source_index < len(packages) and target_index < len(existing_packages):
    source_package = packages[source_index]
    target_package = existing_packages[target_index]

    if source_package == target_package:
        source_index += 1
        target_index += 1
        integrated.append(source_package)
    elif source_package < target_package:
        not_integrated.append(source_package)
        source_index += 1
    else:
        target_index += 1

with open(output_integrated, "w") as f:
    f.write("\n".join(integrated))

with open(output_not_integrated, "w") as f:
    f.write("\n".join(not_integrated))  
