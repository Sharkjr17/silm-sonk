# =========================
# ======= IMPORTS =========
# =========================
import time, random, sys, subprocess, json, math, collections, html, copy
from prompt_toolkit import print_formatted_text as print, HTML, prompt as input
from prompt_toolkit.styles import Style
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.application import run_in_terminal
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.filters import Condition, is_done
from prompt_toolkit.shortcuts import input_dialog, radiolist_dialog
from prompt_toolkit import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.containers import VSplit, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout



with open('data.json', 'r') as file:
    data = json.load(file)


# =========================
# ======= GLOBALS =========
# =========================

PlC = " "
players = {}

# =========================
# ======= HELPERS =========
# =========================



# =========================
# ======= ENTRY POINT =====
# =========================
def start():
    global PlC, game, players

    _ = input("|--Press Enter to Continue--|")
    subprocess.run('clear', shell=True)
    while PlC.isnumeric() == False:
        PlC = input_dialog(title='Welcome', text='Please enter number of players',
            style=Style.from_dict({
                'dialog':             'bg:#88ff88',
                'dialog frame.label': 'bg:#ffffff #000000',
                'dialog.body':        'bg:#000000 #00ff00',
                'dialog shadow':      'bg:#00aa00',
            })
            ).run()
    
    for i in range(int(PlC)):

        _ = input_dialog(title='Input name of player ' + str(i) + ":", text='Please type your name:',
            style=Style.from_dict({
                'dialog':             'bg:#88ff88',
                'dialog frame.label': 'bg:#ffffff #000000',
                'dialog.body':        'bg:#000000 #00ff00',
                'dialog shadow':      'bg:#00aa00',
            })
            ).run()
        players.update({i: {"name": _, "wins": 0, "losses": 0}})
        
    game = radiolist_dialog(title="Welcome", text="Select a Game",
        values=[("Yahtzee", "Yahtzee"),("Blackjack", "Blackjack"),("Chess", "Chess"),("Monopoly", "Monopoly")],
        style=Style.from_dict({
            'dialog':             'bg:#88ff88',
            'dialog frame.label': 'bg:#ffffff #000000',
            'dialog.body':        'bg:#000000 #00ff00',
            'dialog shadow':      'bg:#00aa00',
        })
        ).run()
    print(PlC, game)
    buffer1 = Buffer()  # Editable buffer.

    root_container = VSplit([
        # One window that holds the BufferControl with the default buffer on
        # the left.
        Window(content=BufferControl(buffer=buffer1)),

        # A vertical line in the middle. We explicitly specify the width, to
        # make sure that the layout engine will not try to divide the whole
        # width by three for all these windows. The window will simply fill its
        # content by repeating this character.
        Window(width=1, char='|'),

        # Display the text 'Hello world' on the right.
        Window(content=FormattedTextControl(text='Hello world')),
    ])

    layout = Layout(root_container)

    app = Application(layout=layout, full_screen=True)
    app.run() # You won't be able to Exit this app


if __name__ == "__main__":
    start()
