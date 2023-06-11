# Subtitles Burner
A mini project to burn subtitles into a video files

# About this project
This project is a project for me to practice deployment of a code to burn subtitles using Python (FastAPI)
This project is also for me to learn how to use Streamlit for the first time. Therefore the UI is quite basic, but as I get better in Streamlit, the UI will be improved in the later versions

# Pre-requisites
You will need to install Docker and Docker Compose

# How to use
1. Run `docker-compose up -d`
2. Go to `http://localhost:8501`. You will be in the landing page.
3. Upload your video file and subtitle file (.srt), and click "Run!" button
4. Go to "Status" tab, and your video with subtitles will be displayed.

# Issue
- There is currently a problem with playing the subtitled video
- Video will disappear upon refresh. (Consider using localstate)

# Future Improvements
- User is able to see all processed videos that was requested, unless he/she explicitly delete the video
- Use Nginx as reverse proxy
