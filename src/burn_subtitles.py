import subprocess

import ffmpeg


def fileHasVideoStream(file_path):
    """
    This function checks if the video file is valid
    """
    video_stream = ffmpeg.probe(file_path, select_streams="v")["streams"]

    if video_stream:
        return True
    else:
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
        print(result)
        return False


if __name__ == "__main__":
    burn_subtitles(
        "./examples/input.mp4",
        "./examples/input.srt",
        "./examples/output_hard.mp4",
        force_style="",
    )
