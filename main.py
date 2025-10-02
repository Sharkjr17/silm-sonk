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
from prompt_toolkit.shortcuts import input_dialog, radiolist_dialog
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.containers import VSplit, HSplit, Window, ConditionalContainer
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.document import Document
from prompt_toolkit.layout.margins import ScrollbarMargin
from prompt_toolkit.layout.dimension import Dimension
from prompt_toolkit.application import Application


# =========================     random.choices(list(level.keys()), weights=pathWeight, k=1)    [level[i]["weight"] for i in level]
# ====== LOAD DATA ========
# =========================
with open('data.json', 'r') as file:
    data = json.load(file)


# =========================
# ======= GLOBALS =========
# =========================
DIALOG_STYLE = Style.from_dict({
    'dialog':             'bg:#88ff88',
    'dialog frame.label': 'bg:#ffffff #000000',
    'dialog.body':        'bg:#000000 #00ff00',
    'dialog shadow':      'bg:#00aa00',
})

APP_STYLE = Style.from_dict({
    "background": "bg:#000000 #00ff00",
    "frame.border": "bg:#000000 #00ff00",
    "frame.title": "bg:#88ff88 #000000",
    "titlebar": "bg:#88ff88 #000000",
    "status": "bg:#00aa00 #000000",
    "panel.title": "bg:#000000 #00ff00",
    "panel.body": "bg:#000000 #00ff00",
    "panel.body.a": "bg:#000000 #00ff00",
    "panel.body.b": "bg:#000000 #55ff55",
    "panel.body.c": "bg:#000000 #00ffaa",
    "help": "bg:#001100 #00ff00",
    "help.border": "bg:#001100 #55ff55",
    "label": "bg:#000000 #00ff00",
    "key": "bg:#000000 #00ffaa",
    "value": "bg:#000000 #ffffff",
    "scrollbar": "bg:#000000 #00aa00",  # style for the log scrollbar
})


# =========================
# ======= HELPERS =========
# =========================
def clear_screen():
    cmd = 'cls' if sys.platform.startswith('win') else 'clear'
    subprocess.run(cmd, shell=True)

def prompt_player_count():
    while True:
        value = input_dialog(
            title='Welcome',
            text='Please enter number of players',
            style=DIALOG_STYLE
        ).run()
        if value is None:
            return None
        value = value.strip()
        if value.isdigit() and int(value) > 0:
            return int(value)
        _ = input("Invalid player count. Press Enter to try again...")

def prompt_player_name(index):
    while True:
        name = input_dialog(
            title=f'Input name of player {index}:',
            text='Please type your name:',
            style=DIALOG_STYLE
        ).run()
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
    render_board(data["board"])

def render_board(board_data):
    """
    Render a Monopoly board that scales to the terminal size.
    - GO is bottom-right
    - Board perimeter is 13x13 cells
    - Edge tiles are uniform white spaces
    - Property colors appear one cell inward, facing the board
    """


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

    def make_white_tile(label="?"):
        return Window(
            content=FormattedTextControl(label.center(3)),
            style="bg:#ffffff #000000",
            width=Dimension(weight=1),
            height=Dimension(weight=1),
        )

    def make_corner_tile(label):
        return Window(
            content=FormattedTextControl(label.center(5)),
            style="bg:#ffffff #000000",
            width=Dimension(weight=1),
            height=Dimension(weight=1),
        )

    def make_color_strip(color, orientation="h"):
        """A thin strip of color, 1 unit thick, oriented horizontally or vertically."""
        if orientation == "h":
            return Window(char=" ", style=f"bg:{COLOR_MAP[color]} ",
                          height=Dimension.exact(1), width=Dimension(weight=1))
        else:
            return Window(char=" ", style=f"bg:{COLOR_MAP[color]} ",
                          width=Dimension.exact(1), height=Dimension(weight=1))

    # Build grid
    grid = [[None for _ in range(13)] for _ in range(13)]

    # Mapping of board index to (row,col) around perimeter clockwise starting bottom-right
    coords = []
    for c in range(12, -1, -1):  # bottom row
        coords.append((12, c))
    for r in range(11, -1, -1):  # left col
        coords.append((r, 0))
    for c in range(1, 13):       # top row
        coords.append((0, c))
    for r in range(1, 12):       # right col
        coords.append((r, 12))

    # Place tiles
    for i, (r, c) in enumerate(coords, start=1):
        space = board_data.get(str(i), {"type": "blank", "name": "?"})
        t = space["type"]

        if t == "start":
            grid[r][c] = make_corner_tile("GO")
        elif t == "jail":
            grid[r][c] = make_corner_tile("JAIL")
        elif t == "free parking":
            grid[r][c] = make_corner_tile("FP")
        elif t == "go to jail":
            grid[r][c] = make_corner_tile("G2J")
        else:
            # Default: white tile with label
            grid[r][c] = make_white_tile(space.get("abbr", space.get("name", "?"))[:3])

            # If it's a property, add a color strip inward
            if t == "property":
                if r == 12:   # bottom row → strip above
                    grid[r-1][c] = make_color_strip(space["color"], "h")
                elif r == 0:  # top row → strip below
                    grid[r+1][c] = make_color_strip(space["color"], "h")
                elif c == 0:  # left col → strip right
                    grid[r][c+1] = make_color_strip(space["color"], "v")
                elif c == 12: # right col → strip left
                    grid[r][c-1] = make_color_strip(space["color"], "v")

    # Fill interior with black
    for r in range(13):
        for c in range(13):
            if grid[r][c] is None:
                grid[r][c] = Window(style="bg:#000000",
                                    width=Dimension(weight=1),
                                    height=Dimension(weight=1))

    # Convert to layout
    rows = []
    for r in range(13):
        row_cells = [grid[r][c] for c in range(13)]
        rows.append(VSplit(row_cells, padding=0, height=Dimension(weight=1)))
    root = HSplit(rows, padding=0)

    app = Application(layout=Layout(root), style=APP_STYLE, full_screen=True)
    app.run()





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
        if name is None:
            print(HTML("<ansired>Cancelled while entering player names.</ansired>"))
            return None
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