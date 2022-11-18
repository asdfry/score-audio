FROM python:3.8-slim

COPY . .

RUN pip install --upgrade pip && \
    cat requirements.txt | grep -v '^#' | xargs -n 1 -L 1 pip install --timeout 60 --no-cache-dir

# ENTRYPOINT ["streamlit"]

# CMD ["run", "main.py"]
