from gtts import gTTS
from pathlib import Path
from mutagen.mp3 import MP3
from utils.console import print_step, print_substep
from rich.progress import track

# Durada màxima en segons del vídeo
DURADA = 10

def save_text_to_mp3(reddit_obj):
    """Saves Text to MP3 files.

    Args:
        reddit_obj : The reddit object you received from the reddit API in the askreddit.py file.
    """
    print_step("Saving Text to MP3 files...")
    length = 0

    # Create a folder for the mp3 files.
    Path("assets/mp3").mkdir(parents=True, exist_ok=True)

    # Crea el text en veu
    tts = gTTS(text=reddit_obj["thread_title"], lang="en", slow=False)
    # El guarda en un arxiu
    tts.save(f"assets/mp3/title.mp3")
    # Duració en segons del títol dit per veu
    length += MP3(f"assets/mp3/title.mp3").info.length

    # Crea l'animació de terminal mentre treballa amb cada comentari del thread
    # track() https://rich.readthedocs.io/en/stable/reference/progress.html?highlight=track#rich.progress.track
    # "i" és el comptador de l'iterador, "comment" és el valor de l'objecte sobre el que estem iterant
    for i, comment in track(enumerate(reddit_obj["comments"]), "Saving..."):
        # Surt del bucle quan se sobrepassa la durada màxima
        if length > DURADA:
            break
        # Crea la lectura dels comentaris i els guarda
        tts = gTTS(text=comment["comment_body"], lang="en", slow=False)
        tts.save(f"assets/mp3/{i}.mp3")
        # Actualitza la duració total
        length += MP3(f"assets/mp3/{i}.mp3").info.length

    print_substep("Saved Text to MP3 files successfully.", style="bold green")
    # ! Return the index (que serà el total de comentaris) so we know how many screenshots of comments we need to make.
    return length, i
