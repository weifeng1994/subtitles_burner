import base64
import tempfile

import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import Response

from src.burn_subtitles import burn_subtitles, fileHasVideoStream

app = FastAPI()


# Check docs: Localhost:8000/docs


# Send POST request to localhost:8000/file
@app.post("/file")
async def create_file(
    video_file: UploadFile = File(...), subtitle_file: UploadFile = File(...)
):
    """
    Upload a video file, subtitle file and return a hard subtitled video
    """

    # Check if SRT file extension is correct
    if not subtitle_file.filename.split(".")[-1] == "srt":
        raise HTTPException(
            status_code=415, detail="The file uploaded is not a valid SRT file!"
        )

    # Create temporary directory to store generated files, and they will be removed after returning the output
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Get video extension
        video_ext = video_file.filename.split(".")[-1]
        video_content_type = video_file.content_type

        # Define relevant paths
        input_video_file = f"{tmpdirname}/input_video"
        input_subtitle_file = f"{tmpdirname}/input_subtitles"
        output_video_file = f"{tmpdirname}/output_video.{video_ext}"

        # Read video and subtitles file and write to the respective tempfiles
        video_buffer = await video_file.read()
        subtitle_buffer = await subtitle_file.read()

        with open(input_video_file, "wb") as fv:
            fv.write(video_buffer)

        with open(input_subtitle_file, "wb") as fs:
            fs.write(subtitle_buffer)

        # Check if file is a valid video file
        valid_video_file = fileHasVideoStream(input_video_file)

        # Raise error if the video file is invalid
        if not valid_video_file:
            raise HTTPException(
                status_code=415, detail="The file uploaded is not a valid video file!"
            )

        # Proceed to burn subtitles
        burn_subtitles_succeed = burn_subtitles(
            input_video_file, input_subtitle_file, output_video_file
        )

        if burn_subtitles_succeed:
            # After succeeding, return the video file in base64 format
            with open(output_video_file, "rb") as fo:
                output_video_file_buffer = fo.read()
            import codecs

            # output_video_file_base64 = base64.b64encode(output_video_file_buffer).decode("base64")
            output_video_file_base64 = codecs.encode(
                output_video_file_buffer, "base64"
            ).decode()
            # return output_video_file_base64 in JS readable format. Remove all \n otherwise video won't be loaded
            return (
                f"data:{video_content_type};base64,{output_video_file_base64}".replace(
                    "\n", ""
                )
            )
            # return output_video_file_base64.replace("\n", "")

        else:
            # Inform user that burning of subtitle failed if an error occurs
            raise HTTPException(
                status_code=500, detail="Error during hard subtitling of video"
            )


if __name__ == "__main__":
    # Start server at port 8000
    # Auto restart server whenever there is code change with reload=True
    uvicorn.run(app="src.main:app", host="0.0.0.0", reload=True)

    # Use the following code to start server using HTTPS at port 5006
    # Generate key.pem and cert.pem using this (and answer some qns): openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -sha256

    # uvicorn.run(app="app:app", host='0.0.0.0', port=5006,ssl_keyfile="./key.pem",
    #             ssl_certfile="./cert.pem")
