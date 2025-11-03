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

def overunder(gone):    #return gone.replace("~", " \u0305\u0332") # ‾ _
    match gone:
        case "f":
            return gone.replace("f", HTML("<style background-color='gray'> </style>"))
        case "w":
            return gone.replace("w", HTML("<style background-color='white'> </style>"))
        case "c":
            return gone.replace("c", HTML("<style background-color='white'>c</style>"))
        case "F":
            return gone.replace("F", HTML("<style background-color='white'>F</style>"))
        case "P":
            return gone.replace("P", HTML("<style background-color='white'>P</style>"))
        case _:
            return gone
        

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
def isWin(pc, p):
    check = 0
    for i in range(pc):
        if p[i]["money"] > 0: check += 1
    if check == 1:
        return True
    else: return False

def render_board(board_data, minboard):
    for i in minboard:
        print(HTML("".join([p for p in i])))
        
def pDesc(pc, p):
    for i in range(pc): 
        if p[i]['position'] == "jail": print("jail")
        elif data['board'][p[i]['position']]['type'] == 'property': print(f"{p[i]['name']}-${p[i]['money']}: {p[i]['position']} ({data['board'][p[i]['position']]['color']} property) ({data['board'][p[i]['position']]['name']})")
        elif data['board'][p[i]['position']]['type'] == 'road': print(f"{p[i]['name']}-${p[i]['money']}: {p[i]['position']} (road {data['board'][p[i]['position']]['name']})")
        elif data['board'][p[i]['position']]['type'] == 'utility': print(f"{p[i]['name']}-${p[i]['money']}: {p[i]['position']} (utility {data['board'][p[i]['position']]['name']})")
        else: print(f"{p[i]['name']}-${p[i]['money']}: {p[i]['position']} ({data['board'][p[i]['position']]['type']})")

def posDesc(p):
    if p['position'] == "jail": return "jail"
    elif data['board'][p['position']]['type'] == 'property': return f"{p['position']} ({data['board'][p['position']]['color']} property) ({data['board'][p['position']]['name']})"
    elif data['board'][p['position']]['type'] == 'road': return f"{p['position']} (road {data['board'][p['position']]['name']})"
    elif data['board'][p['position']]['type'] == 'utility': return f"{p['position']} (utility {data['board'][p['position']]['name']})"
    else: return f"{p['position']} ({data['board'][p['position']]['type']})"


def roll():
    dice = []
    dice.append(random.randint(1,6))
    dice.append(random.randint(1,6))
    dice.append(dice[0] + dice[1])
    for i in dice:
        match i:
            case 1: dice.append("⚀")
            case 2: dice.append("⚁")
            case 3: dice.append("⚂")
            case 4: dice.append("⚃")
            case 5: dice.append("⚄")
            case 6: dice.append("⚅")
    return dice

def Property(pos, p):
    if "owned" in pos:
        pass
    else:
        pass

def Road(pos, p):
    global data
    if "owned" not in pos:
        print(f"Road {pos['name']} - Unowned")
        i = input(f"Buy for {pos['price']}? Y/N --> ")
        if i == "Y" & p['money'] >= pos['price']:
            data['board'][p['position']]['owned'] = p['name']
            print(f"{p['name']} succesfully bought {pos['name']}")
            return pos['price']
    elif "owned" in pos & pos['owned'] != p['name']:
        print(f"{pos['name']} is owned by {pos['owned']}")
        pass            
    else:
        print(f"You already own {pos['name']}!")
        

        
            

            


def Utility():
    pass

def Chest():
    pass

def Chance():
    pass

def tax():
    pass

def GTJail():
    pass

def Parking():
    pass

def Start():
    pass

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
        players[i] = {"name": name, "position": "1", "money": 1500}
    _ = input("|--Press Enter to Continue--|")
    clear_screen()
    render_board(data["board"], data["minboard"]) 
    pDesc(player_count, players)   
    _ = input("|--Press Enter to START--|")
    clear_screen()


    pt = 0
    gt = 1
    while isWin(player_count, players) == False:
        render_board(data["board"], data["minboard"])
        pDesc(player_count, players)
        print("\n" + f"Turn {gt}" + "\n" + f"{players[pt]['name']}'s turn: ")
        _ = input("|--Press Enter to ROLL--|")
        clear_screen()
        render_board(data["board"], data["minboard"])
        dice = roll()
        print("\n" + f"{dice[3]} + {dice[4]} = {dice[2]}")
        players[pt]['position'] = str(int(players[pt]['position']) + dice[2])
        print(f"You landed on {posDesc(players[pt])}")
        match data['board'][players[pt]['position']]['type']:
            case "property": Property(data['board'][players[pt]['position']], players[pt])
            case "road": 
                players[pt]["money"] -= Road(data['board'][players[pt]['position']], players[pt])
            case "utility": Utility()
            case "comuntity chest": Chest()
            case "chance": Chance()
            case "income tax": tax()
            case "go to jail": GTJail()
            case "visiting jail": pass
            case "free parking": Parking()
            case "start": Start()
            
        

    




if __name__ == "__main__":
    start()