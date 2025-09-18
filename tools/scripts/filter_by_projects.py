import os

OSS_FUZZ_DIR = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

target_dir =  os.path.join(OSS_FUZZ_DIR, "projects/")
temp_dir =  os.path.join(OSS_FUZZ_DIR, "temp_projects/")
source_file =  os.path.join(OSS_FUZZ_DIR, "tools/scripts/projects_by_language/python_projects.txt")

with open(source_file, "r") as f:
    desired_packages = f.read().splitlines()

if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)

target_dir_projects = sorted(os.listdir(target_dir))
temp_dir_projects = sorted(os.listdir(temp_dir))

for project in target_dir_projects:
    if project not in desired_packages:
        project_path = os.path.join(target_dir, project)
        if os.path.isdir(project_path):
            os.rename(project_path, os.path.join(temp_dir, project))
        else:
            print(f"Error: {project_path} is not a directory.")
for project in temp_dir_projects:
    if project in desired_packages:
        project_path = os.path.join(temp_dir, project)
        if os.path.isdir(project_path):
            os.rename(project_path, os.path.join(target_dir, project))
        else:
            print(f"Error: {project_path} is not a directory.")