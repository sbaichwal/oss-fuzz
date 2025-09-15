import os
import sys
import typer
import google.genai as genai
from dotenv import load_dotenv
import yaml
from pathlib import Path
import shutil

app = typer.Typer()
load_dotenv()

# Load config from OSS-FUZZ root
GOOGLE_API_KEY = os.getenv('google_api_key')

# Configure OSS-FUZZ paths (no hardcoded paths!)
OSS_FUZZ_ROOT = Path(__file__).parent
PROJECT_NAME = "ntia-conformance-checker"
PROJECT_DIR =  "src/oss-fuzz/projects" / PROJECT_NAME

# Configure Gemini
client = genai.Client(api_key=GOOGLE_API_KEY)

def create_project_structure():
    """Create all necessary OSS-Fuzz project files for Python projects"""
    # Create project directory
    PROJECT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Generate project.yaml
    project_yaml = f"""name: {PROJECT_NAME}
main_repo: https://github.com/NTIA/ntia-conformance-checker
language: python
"""
    (PROJECT_DIR / "project.yaml").write_text(project_yaml.strip())
    
    # 2. Generate Dockerfile (Python-specific)
    dockerfile = f"""FROM gcr.io/oss-fuzz-base/base-builder-python

# Clone project
RUN git clone https://github.com/NTIA/ntia-conformance-checker.git /src/{PROJECT_NAME}
WORKDIR /src/{PROJECT_NAME}

# Install dependencies
RUN pip3 install -r requirements.txt

# Copy fuzzer
COPY ntia_conformance_fuzzer.py /src/
"""
    (PROJECT_DIR / "Dockerfile").write_text(dockerfile.strip())
    
    # 3. Generate build.sh (simple Python install)
    build_sh = """#!/bin/bash
set -e

cd /src/ntia-conformance-checker
pip3 install -r requirements.txt
"""
    (PROJECT_DIR / "build.sh").write_text(build_sh.strip())
    os.chmod(PROJECT_DIR / "build.sh", 0o755)
    
    # 4. Generate fuzzer using Gemini
    print("💡 Generating Python fuzzer using Gemini...")
    fuzzer_code = generate_python_fuzzer()
    
    fuzzer_path = PROJECT_DIR / "ntia_conformance_fuzzer.py"
    fuzzer_path.write_text(fuzzer_code)
    
    print(f"\n✅ Generated files in: {PROJECT_DIR}")
    print(f" Test locally with:")
    print(f"   python3 {OSS_FUZZ_ROOT}/infra/helper.py build_fuzzers {PROJECT_NAME}")
    print(f"   python3 {OSS_FUZZ_ROOT}/infra/helper.py run_fuzzer {PROJECT_NAME} ntia_conformance_fuzzer")

def generate_python_fuzzer() -> str:
    """Generate Python fuzzer code using Gemini for NTIA conformance checker"""
    prompt = """
You are an expert in Python fuzzing with OSS-Fuzz and atheris.
The project is NTIA conformance checker (https://github.com/NTIA/ntia-conformance-checker),
which validates Software Bills of Materials (SBOMs) for NTIA compliance.

The main function to fuzz is `check_sbom` in `ntia_conformance_checker.cli`,
which takes a file path as input.

Write a Python fuzzer using:
- `atheris` for fuzzing
- Temporary files to hold fuzzed SBOM data
- Proper exception handling (no crashes)
- Input sanitization (avoid non-UTF8)

Return ONLY the Python code. Do not include explanations.

Here's the expected pattern:
1. Create a temporary file with fuzzed data
2. Call `check_sbom(temp_file_path)`
3. Catch and ignore exceptions
4. Clean up temporary files
"""
    try:
        response = client.models.generate_content(model='gemini-2.0-flash-001', contents=[prompt])
        code = response.text.strip()
        # Clean up any markdown formatting
        code = code.replace("```python", "").replace("```", "").strip()
        return code
    except Exception as e:
        # Fallback to safe template
        return """import sys
import atheris
import os
import tempfile
from ntia_conformance_checker import cli

@atheris.instrument_func
def TestOneInput(data):
    fdp = atheris.FuzzedDataProvider(data)
    # Create temporary file with fuzzed data
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
        tmp.write(fdp.ConsumeBytes(sys.maxsize))
        tmp_path = tmp.name
    
    try:
        # Call the main checker function
        cli.check_sbom(tmp_path)
    except Exception as e:
        # Ignore exceptions — we're fuzzing, not testing error handling
        pass
    finally:
        # Clean up temporary file
        os.unlink(tmp_path)

atheris.Setup(sys.argv, TestOneInput)
atheris.Fuzz()
"""

@app.command()
def onboard():
    """Onboard a new Python project to OSS-Fuzz"""
    print(f"🚀 Starting OSS-Fuzz onboarding for {PROJECT_NAME}...")
    create_project_structure()
    print("\n🎉 Project structure created! Now:")
    print("1. Review all generated files (especially the fuzzer)")
    print("2. Test locally using oss-fuzz's helper scripts")
    print("3. Submit PR to google/oss-fuzz after validation")

if __name__ == "__main__":
    app()