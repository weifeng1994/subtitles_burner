FROM python:3.10

WORKDIR /app

# Modify file size limit of file upload
ENV STREAMLIT_SERVER_MAX_UPLOAD_SIZE="1000"

# Auto reload whenever there are changes to files
ENV STREAMLIT_SERVER_RUN_ON_SAVE=true

COPY . .

RUN pip install streamlit

EXPOSE 8501

CMD ["streamlit", "run", "frontend/app.py"]