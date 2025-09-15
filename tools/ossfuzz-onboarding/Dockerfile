FROM gcr.io/oss-fuzz-base/base-builder

# Install Python dependencies
RUN apt-get update && apt-get install -y python3 python3-pip

# Copy your tool
COPY . /src/ossfuzz-onboard

# Set working directory
WORKDIR /src/ossfuzz-onboard

# Install requirements
RUN pip install -r requirements.txt

# Set entrypoint
ENTRYPOINT ["python", "ossfuzz_onboard.py"]