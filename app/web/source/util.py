import streamlit as st
from PIL import Image


def show_text(dict_res):
    st.write(f"**ID: {dict_res['id']}**")
    st.write(f"Filename: {dict_res['audio']['filename']}")
    st.write(f"Duration: {dict_res['audio']['duration']} sec")
    st.write(f"Elapsed: {dict_res['elapsed']:.2f} sec")
    st.write(f"**Score: {int(dict_res['score']*100)} / 100**")


def show_media(header, audio, image, caption):
    st.header(header)
    bytes = open(audio, "rb").read()
    st.audio(bytes, format="audio/wav")
    img = Image.open(image)
    st.image(img, caption=caption)
