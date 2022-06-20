from random import randrange

from yt_dlp import YoutubeDL

from pathlib import Path
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import *
from utils.console import print_step, print_substep


def get_start_and_end_times(video_length, length_of_clip):
    random_time = randrange(180, int(length_of_clip) - int(video_length))
    return random_time, random_time + video_length


def download_background():
    """Downloads the background video from youtube.

    Shoutout to: bbswitzer (https://www.youtube.com/watch?v=n_Dv4JMiwK8)
    """

    if not Path("assets/mp4/background.mp4").is_file():
        print_step(
            "We need to download the Minecraft background video. This is fairly large but it's only done once."
        )

        print_substep("Downloading the background video... please be patient.")

        ydl_opts = {
            "outtmpl": "assets/mp4/background.mp4",
            "merge_output_format": "mp4",
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download("https://www.youtube.com/watch?v=qu8X8UxBjjM")

        print_substep("Background video downloaded successfully!", style="bold green")

    if not Path("assets/musica/background_music.mp4").is_file():
        print_step(
            "We need to download Lo-Fi music"
        )

        print_substep("Downloading the background music...")

        ydl_opts = {
            "outtmpl": "assets/musica/background_music.mp4",
            "merge_output_format": "mp4",
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download("https://www.youtube.com/watch?v=CWUxKMF2w2U")

        print_substep("Background music downloaded successfully!", style="bold green")


def chop_background_video(video_length):
    print_step("Finding a spot in the background video to chop...")
    background_video = VideoFileClip("assets/mp4/background.mp4")

    start_time, end_time = get_start_and_end_times(video_length, background_video.duration)
    ffmpeg_extract_subclip(
        "assets/mp4/background.mp4",
        start_time,
        end_time,
        targetname="assets/mp4/clip.mp4",
    )

    video = VideoFileClip(os.path.join("assets/musica/background_music.mp4"))
    video.audio.write_audiofile(os.path.join("assets/musica/background_music_mp3.mp3"))

    ffmpeg_extract_subclip(
        "assets/musica/background_music_mp3.mp3",
        start_time,
        end_time,
        targetname="assets/musica/background_music_mp3_clip.mp3",
    )

    print_substep("Background video chopped successfully!", style="bold green")
