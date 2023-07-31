# Subtitles Burner
A mini project to burn subtitles into a video files

# About this project
- This project is a project for me to practice deployment of a code to burn subtitles using Python (FastAPI)
- This project is also for me to learn how to use Streamlit for the first time. Therefore the UI is quite basic, but as I get better in Streamlit, the UI will be improved in the later versions

# Pre-requisites
You will need to install Docker and Docker Compose

# How to use

## API only
1. Run `docker-compose up -d`
2. Go to `http://localhost:8000`. You will be in the landing page of FastAPI
3. Click on the green tab, and click `Try it out`
4. Upload the audio/video file under `media_file` and subtitles file (.srt only) under `subtitles_file`
5. Click `Execute`. FastAPI will show `LOADING`. Wait for it to disappear.
6. Click `Download file` link to download your file! The filename is your original filename prepended by `subtitled_`

## With Frontend (Not Ready, Please use `API only`)
1. Run `docker-compose up -d`
2. Go to `http://localhost:8501`. You will be in the landing page.
3. Upload your video file and subtitle file (.srt), and click "Run!" button
4. Go to "Status" tab, and your video with subtitles will be displayed.

# Note: 
You may now upload an audio file and the app will convert it into an MP4 file using a black image, and burns subtitles into it.

# Issue
- There is currently a problem with playing the subtitled video
- Video will disappear upon refresh. (Consider using localstate)

# Future Improvements
- User is able to see all processed videos that was requested, unless he/she explicitly delete the video
- Use Nginx as reverse proxy