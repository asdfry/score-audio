import os

import requests
import streamlit as st
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="About Classic Demo", page_icon="star", layout="centered")

st.title("About Classic Demo")

upload_file = st.file_uploader(label="Upload audio file", type=["mp3", "mp4", "wav"])

if upload_file:
    bytesio = BytesIO(upload_file.getvalue())
    st.audio(bytesio, format="audio/mpeg")
    use_demucs = st.checkbox(label="Separate vocals and music (This makes longer to run)")
    if st.button(label="RUN"):
        with st.spinner("Processing . . ."):
            res = requests.get(
                os.environ.get("API"),
                params={"use_demucs": use_demucs},
                files={"upload_file": upload_file},
            )
        if res.status_code == 200:
            dict_res = res.json()
            st.success("Done")
            # st.write(f"Sample rate: {dict_res['audio_information']['sample_rate']}")
            st.write(f"Duration: {dict_res['audio_information']['duration']:.2f} sec")
            st.write(f"Elapsed: {dict_res['elapsed']:.2f} sec")
            st.write(f"**Score: {int(dict_res['score']*100)} / 100**")
            img = Image.open("images/result.png")
            st.image(img, caption="Spectrogram with F0")
        else:
            st.error("Fail")