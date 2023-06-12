import tempfile
import codecs

import uvicorn
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, RedirectResponse

from enum import Enum
from src.burn_subtitles import burn_subtitles, fileHasVideoStream

app = FastAPI(
    title="Subtitles Burner",
    description="An application to burn subtitle file into video file"
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
    video_file: UploadFile = File(...),
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
    ori_video_filename = video_file.filename
    # Get video extension
    video_ext = ori_video_filename.split(".")[-1]
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
        if output_type == OutputType.Base64:
        # After succeeding, return the video file in base64 format
            with open(output_video_file, "rb") as fo:
                output_video_file_buffer = fo.read()
            

            output_video_file_base64 = codecs.encode(
                output_video_file_buffer, "base64"
            ).decode()
            # Return in JS readable format. Remove all \n otherwise video won't be loaded
            return (
                f"data:{video_content_type};base64,{output_video_file_base64}".replace(
                    "\n", ""
                )
            )
        else:
            return FileResponse(output_video_file, media_type=video_content_type, filename=f"subtitled_{ori_video_filename}")

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
