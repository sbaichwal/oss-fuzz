import os
from github import Github
from github import Auth
from dotenv import load_dotenv

OSS_FUZZ_DIR = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
output_dir = os.path.join(OSS_FUZZ_DIR, "tools/scripts/script_output")
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
target_file =  os.path.join(OSS_FUZZ_DIR, "tools/scripts/script_output/not_integrated.txt")
output_file = os.path.join(output_dir, "not_integrated_repositories.txt")


with open(target_file, "r") as f:
    lines = f.read().splitlines()

load_dotenv()
auth = Auth.Token(os.getenv("access_token"))

g = Github(auth=auth)

with open(output_file, "w") as f_out:
    for line in lines:
        response = g.search_repositories(query=line, sort="stars", order="desc")
        result = ""
        page = 0

        while page < 10:
            for repo in response.get_page(page):
                if line in repo.full_name:
                    print(repo.full_name)
                    result = repo.html_url
                    page = 11
                    break
            page += 1

        f_out.write(f"{line}: {result}\n")

    