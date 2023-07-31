import codecs
import logging
import tempfile
from enum import Enum

import uvicorn
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, RedirectResponse, StreamingResponse

from src.burn_subtitles import (burn_subtitles, check_file_stream_type,
                                convert_audio_to_video)

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Subtitles Burner",
    description="An application to burn subtitle file into video file",
)


# Define a class to allow user to select input on Swagger UI
class OutputType(str, Enum):
    Files = "Files"
    Base64 = "Base64"


# It seems that the directory and contents are already being released before the FastAPI request is returned.
# However we can use Dependency injection in FastAPI, to inject a temporary directory so that we can return a FileResponse from a tempdir
# Reference: https://stackoverflow.com/questions/72534575/fastapi-fileresponse-cannot-find-file-in-tempdirectory
async def get_temp_dir():
    dir = tempfile.TemporaryDirectory()
    try:
        yield dir.name
    finally:
        del dir


# Send POST request to localhost:8000/file
@app.post("/file")
async def create_file(
    media_file: UploadFile = File(...),
    subtitle_file: UploadFile = File(...),
    output_type: OutputType = OutputType.Files,
    tmpdirname: str = Depends(get_temp_dir),
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
    # with tempfile.TemporaryDirectory() as tmpdirname:
    # Get input video file name
    ori_filename = media_file.filename
    # Get filename without extension
    ori_filename_no_ext = ori_filename.split(".")[0]
    # Get video extension
    media_ext = ori_filename.split(".")[-1]
    media_content_type = media_file.content_type

    # Define relevant paths
    input_file = f"{tmpdirname}/input_file"
    input_converted_file = f"{tmpdirname}/input_converted_file.mp4"
    input_subtitle_file = f"{tmpdirname}/input_subtitles"

    # Read video and subtitles file and write to the respective tempfiles
    video_buffer = await media_file.read()
    subtitle_buffer = await subtitle_file.read()

    with open(input_file, "wb") as fv:
        fv.write(video_buffer)

    with open(input_subtitle_file, "wb") as fs:
        fs.write(subtitle_buffer)

    logging.info("Checking file type ... ")
    # Check if file is a valid video file
    file_stream_type = check_file_stream_type(input_file)

    # Raise error if the video file is invalid
    if not file_stream_type:
        raise HTTPException(
            status_code=415,
            detail="The file uploaded is not a valid video or audio file!",
        )

    if file_stream_type == "audio":
        logging.info("File type is audio! Converting to mp4 ... ")
        # Convert audio file into MP4 by adding a black image
        convert_audio_file_succeed = convert_audio_to_video(
            input_file, input_converted_file
        )

        if not convert_audio_file_succeed:
            raise HTTPException(
                status_code=500, detail="Error converting audio file to video file!"
            )

        output_video_file = f"{tmpdirname}/output_video.mp4"

        logging.info("Burning subtitles ...")
        # Proceed to burn subtitles as mp4 file
        burn_subtitles_succeed = burn_subtitles(
            input_converted_file, input_subtitle_file, output_video_file
        )

        # Changed media extenstion to mp4 as we are outputing a mp4 file
        media_ext = "mp4"
        # Changed media content type to video/mp4 as we are outputing a mp4 file
        media_content_type = "video/mp4"

    else:
        output_video_file = f"{tmpdirname}/output_video.{media_ext}"

        logging.info("File type is video! Burning subtitles ...")
        # Proceed to burn subtitles
        burn_subtitles_succeed = burn_subtitles(
            input_file, input_subtitle_file, output_video_file
        )

    if burn_subtitles_succeed:
        if output_type == OutputType.Base64:
            # After succeeding, return the video file in base64 format
            with open(output_video_file, "rb") as fo:
                output_video_file_buffer = fo.read()

            output_video_file_base64 = codecs.encode(
                output_video_file_buffer, "base64"
            ).decode()
            # Return in JS readable format. Remove all \n otherwise video won't be loaded
            return (
                f"data:{media_content_type};base64,{output_video_file_base64}".replace(
                    "\n", ""
                )
            )
        else:

            def iterfile():
                CHUNK_SIZE = 1024 * 1024  # = 1MB - adjust the chunk size as desired
                with open(output_video_file, "rb") as f:
                    while chunk := f.read(CHUNK_SIZE):
                        yield chunk

            headers = {
                "Content-Disposition": f'attachment; filename="subtitled_{ori_filename_no_ext}.{media_ext}"'
            }
            return StreamingResponse(
                iterfile(), headers=headers, media_type="application/octet-stream"
            )
            # return FileResponse(output_video_file, media_type=media_content_type, filename=f"subtitled_{ori_filename}")

    else:
        # Inform user that burning of subtitle failed if an error occurs
        raise HTTPException(
            status_code=500, detail="Error during hard subtitling of video"
        )


@app.get("/", include_in_schema=False)
def redirect_response():
    # Redirect response to "/docs" if user hit the "/" endpoint. Set include_in_schema=False to exclude this endpoint from displaying in Swagger UI
    return RedirectResponse("/docs")


if __name__ == "__main__":
    # Start server at port 8000
    # Auto restart server whenever there is code change with reload=True
    uvicorn.run(app="src.main:app", host="0.0.0.0", reload=True)

    # Use the following code to start server using HTTPS at port 5006
    # Generate key.pem and cert.pem using this (and answer some qns): openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -sha256

    # uvicorn.run(app="app:app", host='0.0.0.0', port=5006,ssl_keyfile="./key.pem",
    #             ssl_certfile="./cert.pem")
