FROM pytorch/pytorch:1.12.1-cuda11.3-cudnn8-runtime

COPY . .

RUN apt-get update && apt-get install -y ffmpeg && \
    pip install --upgrade pip && \
    cat requirements.txt | grep -v '^#' | xargs -n 1 -L 1 pip install --timeout 60 --no-cache-dir

# ENTRYPOINT ["/bin/bash", "-i", "-c"]

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
