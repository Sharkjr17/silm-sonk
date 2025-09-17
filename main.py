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


# =========================
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

# App style (keeps the green-on-black feel, with accents similar to your dialogs)
APP_STYLE = Style.from_dict({
    # Base background + default text
    'background':               'bg:#000000 #00ff00',
    'frame.border':             'bg:#000000 #00ff00',
    'frame.title':              'bg:#88ff88 #000000',
    # Title bar and status bar
    'titlebar':                 'bg:#88ff88 #000000',
    'status':                   'bg:#00aa00 #000000',
    # Panels
    'panel.title':              'bg:#000000 #00ff00',
    'panel.body':               'bg:#000000 #00ff00',
    # Accents (cycled via keybinding)
    'accent.a':                 'bg:#000000 #00ff00',
    'accent.b':                 'bg:#000000 #55ff55',
    'accent.c':                 'bg:#000000 #00ffaa',
    # Help overlay
    'help':                     'bg:#001100 #00ff00',
    'help.border':              'bg:#001100 #55ff55',
    # Keys and labels
    'label':                    'bg:#000000 #00ff00',
    'key':                      'bg:#000000 #00ffaa',
    'value':                    'bg:#000000 #ffffff',
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

def prompt_game_selection():
    return radiolist_dialog(
        title="Welcome",
        text="Select a Game",
        values=[
            ("Yahtzee", "Yahtzee"),
            ("Blackjack", "Blackjack"),
            ("Chess", "Chess"),
            ("Monopoly", "Monopoly"),
        ],
        style=DIALOG_STYLE
    ).run()


# =========================
# ===== GAME HANDLERS =====
# =========================
def play_yahtzee(players, data):
    print(HTML(f"<ansigreen>Starting Yahtzee with {len(players)} player(s).</ansigreen>"))

def play_blackjack(players, data):
    print(HTML(f"<ansigreen>Starting Blackjack with {len(players)} player(s).</ansigreen>"))

def play_chess(players, data):
    print(HTML(f"<ansigreen>Starting Chess with {len(players)} player(s).</ansigreen>"))

def play_monopoly(players, data):
    print(HTML(f"<ansigreen>Starting Monopoly with {len(players)} player(s).</ansigreen>"))


GAMES_DISPATCHER = {
    "Yahtzee": play_yahtzee,
    "Blackjack": play_blackjack,
    "Chess": play_chess,
    "Monopoly": play_monopoly,
}


# =========================
# === CAPABILITIES SCREEN ==
# =========================
def show_capabilities_screen(session):
    """
    Full-screen prompt_toolkit Application showing:
    - Selected game and players
    - Capability list
    - Scrollable log output
    - Status bar (clock)
    - Help overlay
    Keybindings: F1 (help), A (add log), C (cycle accent), Tab (focus), Q/Esc (exit)
    """
    players = session["players"]
    game = session["game"]

    # Mutable app state
    state = {
        "accent": "accent.a",
        "show_help": False,
        "logs": ["Session initialized.", f"Game selected: {game}.", f"Players: {len(players)}."],
        "focus_index": 0,  # 0=left, 1=right
    }

    # Left: session info + capabilities
    def _player_lines():
        for i, pdata in players.items():
            yield ("class:label", f"  {i}: ")
            yield ("class:value", f"{pdata['name']}")
            yield ("", "\n")

    left_title = FormattedTextControl(lambda: [
        ("class:panel.title", f"  Session ({game})  "),
    ])
    left_body = FormattedTextControl(lambda: list(_player_lines()) + [
        ("", "\n"),
        ("class:panel.title", "  Capabilities  "),
        ("", "\n"),
        ("class:label", "  • "),
        ("", "Full-screen layout (HSplit/VSplit)\n"),
        ("class:label", "  • "),
        ("", "Styled panels and borders\n"),
        ("class:label", "  • "),
        ("", "Formatted text with dynamic accents\n"),
        ("class:label", "  • "),
        ("", "Scrollable log buffer\n"),
        ("class:label", "  • "),
        ("", "Keybindings (F1, A, C, Tab, Q/Esc)\n"),
        ("class:label", "  • "),
        ("", "Status bar with live clock\n"),
    ])

    left_panel = HSplit([
        Window(height=1, content=left_title, style="class:frame.title"),
        Window(
            content=left_body,
            style=lambda: f"class:panel.body {state['accent']}",
            wrap_lines=False,
            always_hide_cursor=True
        ),
    ], style="class:frame.border")

    # Right: scrollable log
    log_buffer = Buffer(read_only=True)
    def refresh_log_text():
        log_buffer.text = "\n".join(state["logs"])
    refresh_log_text()

    right_title = FormattedTextControl(lambda: [
        ("class:panel.title", "  Event log  "),
    ])
    right_panel = HSplit([
        Window(height=1, content=right_title, style="class:frame.title"),
        Window(BufferControl(buffer=log_buffer), style="class:panel.body", wrap_lines=False),
    ], style="class:frame.border")

    # Title bar and status bar
    titlebar = Window(
        height=1,
        content=FormattedTextControl(lambda: [
            ("class:titlebar", "  Game Control Center "),
            ("", "— "),
            ("class:label", "F1"),
            ("", " Help  "),
            ("class:label", "A"),
            ("", " Add log  "),
            ("class:label", "C"),
            ("", " Accent  "),
            ("class:label", "Tab"),
            ("", " Focus  "),
            ("class:label", "Q/Esc"),
            ("", " Exit"),
        ]),
        style="class:titlebar",
        always_hide_cursor=True
    )

    def _clock_text():
        return time.strftime("%H:%M:%S")

    statusbar = Window(
        height=1,
        content=FormattedTextControl(lambda: [
            ("class:status", f"  Players: {len(players)}  "),
            ("", " | "),
            ("class:status", f"Game: {game}  "),
            ("", " | "),
            ("class:status", f"Time: {_clock_text()}  "),
        ]),
        style="class:status",
        always_hide_cursor=True
    )

    # Help overlay
    help_lines = [
        ("class:help.border", " Help ".center(40, "—")),
        ("", "\n\n"),
        ("class:key", "F1"), ("", " Toggle help\n"),
        ("class:key", "A"), ("", " Append a demo log entry\n"),
        ("class:key", "C"), ("", " Cycle accent color\n"),
        ("class:key", "Tab"), ("", " Switch focus left/right\n"),
        ("class:key", "Q / Esc"), ("", " Exit screen\n"),
    ]
    help_window = ConditionalContainer(
        content=Window(FormattedTextControl(lambda: help_lines), style="class:help", always_hide_cursor=True),
        filter=Condition(lambda: state["show_help"])
    )

    # Root layout
    body = VSplit(
        [
            left_panel,
            Window(width=1, char="│", style="class:frame.border"),
            right_panel,
        ],
        padding=0,
        style="class:background"
    )
    root = HSplit([titlebar, body, statusbar, help_window])

    # Keybindings
    kb = KeyBindings()

    @kb.add("f1")
    def _(event):
        state["show_help"] = not state["show_help"]

    @kb.add("a")
    def _(event):
        state["logs"].append(f"[{_clock_text()}] Demo log entry (#{len(state['logs'])+1})")
        refresh_log_text()

    @kb.add("c")
    def _(event):
        order = ["accent.a", "accent.b", "accent.c"]
        idx = (order.index(state["accent"]) + 1) % len(order)
        state["accent"] = order[idx]

    @kb.add("tab")
    def _(event):
        state["focus_index"] = 1 - state["focus_index"]
        event.app.layout.focus(right_panel if state["focus_index"] else left_panel)

    @kb.add("q")
    @kb.add("escape")
    def _(event):
        event.app.exit()

    # Application
    app = Application(
        layout=Layout(root, focused_element=left_panel),
        key_bindings=kb,
        style=APP_STYLE,
        full_screen=True,
        mouse_support=False
    )
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

    game = prompt_game_selection()
    if game is None:
        print(HTML("<ansired>No game selected. Exiting.</ansired>"))
        return None

    print(HTML(f"<ansiyellow>Players: {player_count}, Game: {game}</ansiyellow>"))
    return {"players": players, "game": game}


def dispatch_game(session):
    # Show the full-screen capabilities screen first
    show_capabilities_screen(session)

    # Then proceed to the selected game (optional; comment out if you want to return to menu instead)
    game = session["game"]
    players = session["players"]
    handler = GAMES_DISPATCHER.get(game)
    if handler:
        handler(players, data)
    else:
        print(HTML(f"<ansired>Unknown game selection: {game}</ansired>"))


if __name__ == "__main__":
    session = start()
    if session:
        dispatch_game(session)