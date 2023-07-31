import logging
import subprocess

import ffmpeg

logging.basicConfig(level=logging.INFO)


def check_file_stream_type(file_path):
    """
    This function checks if the file is a valid video or audio
    """
    video_stream = ffmpeg.probe(file_path, select_streams="v")["streams"]

    if video_stream:
        return "video"
    else:
        audio_stream = ffmpeg.probe(file_path, select_streams="a")["streams"]
        if audio_stream:
            return "audio"
        else:
            return None


def convert_audio_to_video(
    input_file, output_file, background_path="./asset/black_background.png"
):
    """
    This function converts audio file to video file by adding a black background
    """
    cmd = f"ffmpeg -f lavfi -i color=c=black:s=1280x720 -i {input_file} -shortest -fflags +shortest {output_file}"
    # cmd = f'ffmpeg -y -loop 1 -i {background_path} -i {input_file} -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:-1:-1:color=black,setsar=1,format=yuv420p" -shortest -fflags +shortest {output_file}'
    # Uses an actual background image as ffmpeg-python does not recognize color=c=black:s=1280x720, and will throw file not found error
    # cmd = f"ffmpeg -f lavfi -i {background_path} -i {input_file} -shortest -fflags +shortest {output_file}"
    # logging.info("Adding background image ... ")
    logging.info(cmd)
    result = subprocess.run(cmd, capture_output=True, shell=True)
    if result.returncode == 0:
        return True
    else:
        logging.error(result)
        return False


def burn_subtitles(input_file, subtitle_file, output_file, force_style=""):
    """
    This functions 'burns' subtitle into the video file
    """
    # force_style = ":force_style='Fontname=Futura,PrimaryColour=&HFF00'"
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        input_file,
        "-vf",
        f"subtitles={subtitle_file}{force_style}",
        output_file,
    ]

    result = subprocess.run(cmd, capture_output=True)
    if result.returncode == 0:
        return True
    else:
        logging.info(result)
        return False


if __name__ == "__main__":
    burn_subtitles(
        "./examples/input.mp4",
        "./examples/input.srt",
        "./examples/output_hard.mp4",
        force_style="",
    )
