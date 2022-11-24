import json
import os
from pathlib import Path

import requests
import streamlit as st

from util import show_text, show_media

st.set_page_config(page_title="Score Audio Demo", page_icon="musical_note", layout="centered")

st.title("Score Audio Demo")

options = ["Upload file", "Input ID"]
option = st.sidebar.radio(
    "Select option",
    options
)

if option == options[0]:
    upload_file = st.file_uploader(label="Upload audio file", type=["mp3", "mp4", "wav"])
    use_demucs = st.checkbox(label="Separate vocals and music (This makes longer to run)")

    if upload_file:
        bytes = upload_file.getvalue()
        st.audio(bytes, format="audio/mpeg")

    if st.button(label="RUN"):
        with st.spinner("Processing . . ."):
            res = requests.post(
                os.environ.get("API"),
                params={"use_demucs": use_demucs},
                files={"upload_file": upload_file},
            )

        if res.status_code == 200:
            dict_res = res.json()
            show_text(dict_res)  # ID, Duration, Elapsed, Score
            id = dict_res["id"]
            if use_demucs:
                show_media(
                    header="Vocal",
                    audio=os.path.join(os.environ.get("STORAGE_DIR"), id, "result.wav"),
                    image=os.path.join(os.environ.get("STORAGE_DIR"), id, "result.png"),
                    caption="Spectrogram(vocal) with F0",
                )
                show_media(
                    header="Accompaniment",
                    audio=os.path.join(os.environ.get("STORAGE_DIR"), id, "accom.wav"),
                    image=os.path.join(os.environ.get("STORAGE_DIR"), id, "accom.png"),
                    caption="Spectrogram(accompaniment)",
                )
            else:
                show_media(
                    header="Result",
                    audio=os.path.join(os.environ.get("STORAGE_DIR"), id, "result.wav"),
                    image=os.path.join(os.environ.get("STORAGE_DIR"), id, "result.png"),
                    caption="Spectrogram with F0",
                )
        else:
            st.error("Fail")

elif option == options[1]:
    id = st.text_input("Input job ID")

    if st.button(label="SEARCH"):
        with st.spinner("Processing . . ."):
            result_json = os.path.join(os.environ.get("STORAGE_DIR"), id, "result.json")
            if not Path(result_json).exists():
                st.error("Invalid ID")
            else:
                with open(result_json, "r") as f:
                    dict_res = json.load(f)
                show_text(dict_res)  # ID, Duration, Elapsed, Score
                
                if Path(os.path.join(os.environ.get("STORAGE_DIR"), id, "accom.wav")).exists():
                    show_media(
                        header="Vocal",
                        audio=os.path.join(os.environ.get("STORAGE_DIR"), id, "result.wav"),
                        image=os.path.join(os.environ.get("STORAGE_DIR"), id, "result.png"),
                        caption="Spectrogram(vocal) with F0",
                    )
                    show_media(
                        header="Accompaniment",
                        audio=os.path.join(os.environ.get("STORAGE_DIR"), id, "accom.wav"),
                        image=os.path.join(os.environ.get("STORAGE_DIR"), id, "accom.png"),
                        caption="Spectrogram(accompaniment)",
                    )
                else:
                    show_media(
                        header="Result",
                        audio=os.path.join(os.environ.get("STORAGE_DIR"), id, "result.wav"),
                        image=os.path.join(os.environ.get("STORAGE_DIR"), id, "result.png"),
                        caption="Spectrogram with F0",
                    )
