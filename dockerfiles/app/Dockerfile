FROM python:3.10

RUN apt update && apt install -y ffmpeg

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["python", "-m", "src.main"]