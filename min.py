# =========================
# ======= IMPORTS =========
# =========================
import time, random, sys, subprocess, json, math, collections, html, copy
from prompt_toolkit import print_formatted_text as print, HTML, prompt as input
from prompt_toolkit.styles import Style
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.application import run_in_terminal, get_app, Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.filters import Condition, is_done

# =========================
# ====== LOAD DATA ========
# =========================

with open('data.json', 'r') as file:
    data = json.load(file)



# =========================
# ======= HELPERS =========
# =========================

def clear_screen():
    cmd = 'cls' if sys.platform.startswith('win') else 'clear'
    subprocess.run(cmd, shell=True)

def bottom_toolbar():
    return HTML('This is a <b><style bg="ansired">Toolbar</style></b>!')



def prompt_player_count():
    while True:
        value = input(HTML("<b>How Many Players? --> </b>"), bottom_toolbar=bottom_toolbar())
        if value is None:
            return None
        value = value.strip()
        if value.isdigit() and int(value) > 0:
            return int(value)
        _ = input("Invalid player count. Press Enter to try again...")

def prompt_player_name(i):
    while True:
        name = input(HTML(f"<b>Input Name for Player {i} --> </b>"))
        if name is None:
            return None
        name = name.strip()
        if name:
            return name
        _ = input("Name cannot be empty. Press Enter to try again...")

# =========================
# ===== GAME HANDLER ======
# =========================

def play_monopoly(players, data):
    print(HTML(f"<ansigreen>Starting Monopoly with {len(players)} player(s).</ansigreen>"))
    render_board(data["board"], data["minboard"])

def render_board(board_data, minboard):
    COLOR_MAP = {
        "brown": "#8B4513",
        "red": "#FF0000",
        "orange": "#FFA500",
        "purple": "#800080",
        "yellow": "#FFFF00",
        "pink": "#FFC0CB",
        "green": "#008000",
        "blue": "#0000FF",
    }
    
    for i in range(minboard):
        for e in minboard[i]:
            print(e, end="")
        






# =========================
# ======= ENTRY POINT =====
# =========================

def start():
    _ = input("|--Press Enter to Continue--|")
    clear_screen()

    player_count = prompt_player_count()
    if player_count is None:
        print(HTML("<ansired>Cancelled at player count.</ansired>"))
        return None

    players = {}
    for i in range(player_count):
        name = prompt_player_name(i)
        players[i] = {"name": name, "wins": 0, "losses": 0}

    game = "Monopoly"  # fixed
    print(HTML(f"<ansiyellow>Players: {player_count}, Game: {game}</ansiyellow>"))
    return {"players": players, "game": game}


def dispatch_game(session):
    # Always launch Monopoly
    play_monopoly(session["players"], data)

if __name__ == "__main__":
    session = start()
    if session:
        dispatch_game(session)