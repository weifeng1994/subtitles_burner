import base64
import os

import requests
import streamlit as st

endpoint = "http://app:8000/file"

# Initialization
if "file_base64" not in st.session_state:
    st.session_state["file_base64"] = None
    st.session_state["file_processed"] = False


def call_api(video_file, subtitles_file):
    resp = requests.post(
        endpoint, params={"output_type": "Base64"}, files={"video_file": video_file, "subtitle_file": subtitles_file}
    )

    if resp.status_code == 200:
        return resp.text


def display_run_button(disabled):
    """
    Making button conditional so that the callback function doesn't run before button is clicked while using "on_click"
    """
    placeholder = st.empty()
    # Create a button for user to click. The "key" argument is to generate unique buttons.
    run_button = placeholder.button("Run!", disabled=disabled, key="1")
    if run_button:
        # Disable button while running API calls
        placeholder.button("Processing!", disabled=True, key="2")
        # Call API to get file in base64 format
        file_base64 = call_api(video_file, subtitles_file)
        # Enable button after API calls
        placeholder.button("Run!", disabled=False, key="3")

        return file_base64


st.title("Subtitle Burner :fire:")

tab_1, tab_2 = st.tabs(["Upload", "Status"])

with tab_1:
    video_file = st.file_uploader("Please upload your video file:", key="video_file")
    subtitles_file = st.file_uploader(
        "Please upload your subtitle file:", key="subtitles_file"
    )

    # run_button = st.button("Run!", on_click=call_api("Hello")) # This runs even when button is not clicked
    if video_file and subtitles_file:
        # Enables button after both files are uploaded and run a POST request to get the document in base64 format
        file_base64 = display_run_button(False)
        st.session_state["file_base64"] = file_base64
        st.session_state["file_processed"] = True
    else:
        # Disabled button
        display_run_button(True)


with tab_2:
    if (
        st.session_state["file_processed"]
        and st.session_state["video_file"]
        and st.session_state["subtitles_file"]
    ):
        st.markdown(f"**Video Filename:** {st.session_state['video_file'].name}")
        st.markdown(f"**Subtitle Filename:** {st.session_state['subtitles_file'].name}")

    if st.session_state["file_base64"]:
        # st.markdown(get_binary_file_downloader_html(st.session_state["file_base64"]), unsafe_allow_html=True)
        download_video_filename = f'processed_{st.session_state["video_file"].name}'
        video_html = (
            f'<video controls><source src={st.session_state["file_base64"]}></video>'
        )
        st.markdown(video_html, unsafe_allow_html=True)
        # st.download_button('Download Here', st.session_state["file_base64"], download_video_filename)
        # TODO: Currently file_base64 information is lost after clicking Download button. Removing all other information

    else:
        # Disable button if there are no value for file_base64
        st.write(
            "There are currently no videos being uploaded. You may upload a video using the 'Upload' tab."
        )
        st.session_state["file_processed"] = False
