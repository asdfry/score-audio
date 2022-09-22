FROM python:3.8-slim

COPY . .

RUN apt-get update && apt-get install -y git wget ffmpeg python3-pip && \
    cat requirements.txt | grep -v '^#' | xargs -n 1 -L 1 pip install --timeout 60 --no-cache-dir && \
    git clone -b main --single-branch https://github.com/facebookresearch/demucs && \
    cd demucs && python3 -m pip install -e . && \
    python3 -m demucs.separate test.mp3 && \
    rm -r separated

# ENTRYPOINT ["/bin/bash", "-i", "-c"]

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
