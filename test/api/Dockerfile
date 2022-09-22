FROM nvidia/cuda:11.1.1-cudnn8-runtime-ubuntu18.04

COPY . .

RUN apt-get update && apt-get install -y git wget ffmpeg python3.8 python3.8-distutils && \
    wget https://bootstrap.pypa.io/get-pip.py && python3.8 get-pip.py && \
    cat requirements.txt | grep -v '^#' | xargs -n 1 -L 1 pip install --timeout 60 --no-cache-dir && \
    pip install torch==1.10.1+cu111 torchaudio==0.10.1+cu111 -f https://download.pytorch.org/whl/torch_stable.html && \
    git clone -b main --single-branch https://github.com/facebookresearch/demucs && \
    cd demucs && python3.8 -m demucs.separate test.mp3 && \
    rm -r separated

# ENTRYPOINT ["/bin/bash", "-i", "-c"]

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
