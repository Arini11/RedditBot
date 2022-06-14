from praw.models import MoreComments
from rich.console import Console
from rich.progress import track

from utils.console import print_markdown, print_step, print_substep
from dotenv import load_dotenv
from python_translator import Translator

console = Console()
import os, random, praw, re


def get_subreddit_threads():
    global submission
    """
    Returns a list of threads from the AskReddit subreddit.
    """

    load_dotenv()

    if os.getenv("REDDIT_2FA", default="no").casefold() == "yes":
        print(
            "\nEnter your two-factor authentication code from your authenticator app.\n"
        )
        code = input("> ")
        print()
        pw = os.getenv("REDDIT_PASSWORD")
        passkey = f"{pw}:{code}"
    else:
        passkey = os.getenv("REDDIT_PASSWORD")

    content = {}
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent="Accessing AskReddit threads",
        username=os.getenv("REDDIT_USERNAME"),
        password=passkey,
    )

    # If the user specifies that he doesnt want a random thread, or if he doesn't insert the "RANDOM_THREAD" variable at all, ask the thread link
    if not os.getenv("RANDOM_THREAD") or os.getenv("RANDOM_THREAD") == "no":
        print_substep("Insert the full thread link:", style="bold green")
        thread_link = input()
        print_step(f"Getting the inserted thread...")
        submission = reddit.submission(url=thread_link)
    else:
        # Otherwise, picks a random thread from the inserted subreddit
        if os.getenv("SUBREDDIT"):
            subreddit = reddit.subreddit(re.sub(r"r\/", "", os.getenv("SUBREDDIT")))
        else:
            # ! Prompt the user to enter a subreddit
            try:
                subreddit = reddit.subreddit(
                    re.sub(r"r\/", "", input("What subreddit would you like to pull from? "))
                )
            except ValueError:
                subreddit = reddit.subreddit("askreddit")
                print_substep("Subreddit not defined. Using AskReddit.")

        threads = subreddit.hot(limit=25)
        submission = list(threads)[random.randrange(0, 25)]

    print_substep(f"Video will be: {submission.title} :thumbsup:")
    console.log("Getting video comments...")
    # print(vars(submission))
    try:
        content["thread_url"] = submission.url
        content["thread_title"] = submission.title
        content["thread_post"] = submission.selftext
        content["comments"] = []

        for top_level_comment in submission.comments:
            # print(vars(top_level_comment))
            if not top_level_comment.stickied:
                content["comments"].append(
                    {
                        "comment_body": top_level_comment.body,
                        "comment_url": top_level_comment.permalink,
                        "comment_id": top_level_comment.id,
                        "comment_author": top_level_comment.author
                    }
                )

    except AttributeError as e:
        print(e)
        pass

    print_substep("Received AskReddit threads successfully.", style="bold green")

    return content


def traduir(reddit_object):
    translator = Translator()

    # Traduir títol
    titol = reddit_object["thread_title"]
    reddit_object["thread_title"] = str(translator.translate(titol, "spanish", "english"))

    # Traduir comentaris
    # console.log("Traduint comentaris...")
    max = 5  # Màxim de comentaris a traduir, de moment ho limitem, si no tarda massa a fer totes les traduccions
    for i, c in track(enumerate(reddit_object["comments"]), "Traduint...", style="bold yellow"):
        if i >= max: break
        comment_body = c["comment_body"]
        c["comment_body"] = str(translator.translate(comment_body, "spanish", "english"))


def generarHTML(reddit_object):
    print(reddit_object["thread_url"])
    html_inici = """
    <html>
    <head>
      <link rel="stylesheet" type="text/css" href="estils.css">
    </head>
    <body>
      <div class="main-container">
      <div class="heading">
        <h1 class="heading__title">--titol--</h1>
      </div>
      <div class="cards">
    """.replace("--titol--",reddit_object["thread_title"])
    html_final = """
      </div>
    </div>
    </body>

    </html>
    """
    html = ""

    compt = 5  # Ho limito a 5 per fer proves
    # submission.comments obté tots els top-level comments
    for top_level_comment in reddit_object["comments"]:
        if compt <= 0: break
        compt -= 1

        # Dins de comments hi ha diferents tipus d'objectes. Comment són els comentaris normals MoreComments són objectes
        # que contenen els comentaris que es carregarien al clicar "mostrar més comentaris"/"load more..." Com que només
        # volem obtenir uns quants comentaris, no cal fer cas als MoreComments, en tenim prou amb els Comment sols. Si
        # trobem un MoreComments, l'ingnorem
        if isinstance(top_level_comment, MoreComments):
            continue

        # Objecte Comment https://praw.readthedocs.io/en/stable/code_overview/models/comment.html
        # Ens interessen els següents atribus: body, author, created_utc
        if top_level_comment["comment_body"] == '[deleted]':
            continue

        # S'ha de fer un try catch, perquè si hi ha usuaris que tenen el compte eliminat, o han fet comentaris que
        # posteriorment s'han eliminat, quan s'intenti accedir a alguns atributs, petarà perquè l'objecte Redditor o
        # Comment tindran atributs nulls.
        try:
            body = top_level_comment["comment_body"]
            # data = top_level_comment.created_utc
            html += """
                <div class="card">
                  <div class="card__icon"><i class="fas fa-bolt"></i></div>
                  <p class="card__exit"><i class="fas fa-times"></i></p>
                  <h2 class="card__title">--body--</h2>
                  <p class="card__apply">
                    <a class="card__link" href="#">--autor--<i class="fas fa-arrow-right"></i></a>
                  </p>
                </div>  
            """
            html = html.replace("--body--", body)

            autor = top_level_comment["comment_author"]
            html = html.replace("--autor--", autor.name)
            # No sé perquè diu que icon_img no existeix a redditor.
            # redditor = reddit.redditor(autor)
            # autor_nom = redditor.name
            # autor_avatar = redditor.icon_img

        except Exception as e:
            print("peta" + str(compt))
            print(e)
            # html += '<p>' + "Deleted" + '</p>' + '<p>' +
            # "https://www.redditstatic.com/avatars/defaults/v2/avatar_default_0.png" + '</p>'
            pass
        # html += '</div>'
    #
    f = open('html-test.html', 'w')
    f.write(html_inici + html + html_final)
    f.close()
