import os, sys, re, random, types, json, copy, time, importlib, keyboard, string, secrets
from collections import Counter
from inputimeout import inputimeout, TimeoutOccurred
from datetime import datetime
battleLogFile = None
_simBattleCounter = 0
maxBattleLogs = 20

Color = {
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[34m",
    "magenta": "\033[95m",
    "cyan": "\033[36m",
    "white": "\033[97m",
    "line": "\033[4m",
    "reset": "\033[0m"
}

symbols = {
        "Weak": f"{Color['red']}xXx{Color['reset']}",
        "Super Weak": f"{Color['red']}X{Color['yellow']}!{Color['red']}X{Color['reset']}",
        "Neutral": f"-N-",
        "Resist": f"{Color['green']}xNx{Color['reset']}",
        "Null": f"{Color['magenta']}oØo{Color['reset']}",
        "Reflect": f"{Color['yellow']}xRx{Color['reset']}",
        "Absorb": f"{Color['blue']}xAx{Color['reset']}"
}   

elements = {
    "fire": {
        "Weak": f"{Color['red']}Weak{Color['reset']}",
        "Super Weak": f"{Color['red']}Super Weak{Color['reset']}",
        "Neutral": "Neutral",
        "Resist": f"{Color['green']}Resist{Color['reset']}",
        "Null": f"{Color['magenta']}Null{Color['reset']}",
        "Reflect": f"{Color['yellow']}Reflect{Color['reset']}",
        "Absorb": f"{Color['blue']}Absorb{Color['reset']}"
    },

    "ice": {
        "Weak": f"{Color['red']}Weak{Color['reset']}",
        "Super Weak": f"{Color['red']}Super Weak{Color['reset']}",
        "Neutral": "Neutral",
        "Resist": f"{Color['green']}Resist{Color['reset']}",
        "Null": f"{Color['magenta']}Null{Color['reset']}",
        "Reflect": f"{Color['yellow']}Reflect{Color['reset']}",
        "Absorb": f"{Color['blue']}Absorb{Color['reset']}"
    },

    "wind": {
        "Weak": f"{Color['red']}Weak{Color['reset']}",
        "Super Weak": f"{Color['red']}Super Weak{Color['reset']}",
        "Neutral": "Neutral",
        "Resist": f"{Color['green']}Resist{Color['reset']}",
        "Null": f"{Color['magenta']}Null{Color['reset']}",
        "Reflect": f"{Color['yellow']}Reflect{Color['reset']}",
        "Absorb": f"{Color['blue']}Absorb{Color['reset']}"
    },

    "thunder": {
        "Weak": f"{Color['red']}Weak{Color['reset']}",
        "Super Weak": f"{Color['red']}Super Weak{Color['reset']}",
        "Neutral": "Neutral",
        "Resist": f"{Color['green']}Resist{Color['reset']}",
        "Null": f"{Color['magenta']}Null{Color['reset']}",
        "Reflect": f"{Color['yellow']}Reflect{Color['reset']}",
        "Absorb": f"{Color['blue']}Absorb{Color['reset']}"
    },

    "mighty": {
        "Weak": f"{Color['red']}Weak{Color['reset']}",
        "Super Weak": f"{Color['red']}Super Weak{Color['reset']}",
        "Neutral": "Neutral",
        "Resist": f"{Color['green']}Resist{Color['reset']}",
        "Null": f"{Color['magenta']}Null{Color['reset']}",
        "Reflect": f"{Color['yellow']}Reflect{Color['reset']}",
        "Absorb": f"{Color['blue']}Absorb{Color['reset']}"
    },

    "physical": {
        "Weak": f"{Color['red']}Weak{Color['reset']}",
        "Super Weak": f"{Color['red']}Super Weak{Color['reset']}",
        "Neutral": "Neutral",
        "Resist": f"{Color['green']}Resist{Color['reset']}",
        "Null": f"{Color['magenta']}Null{Color['reset']}",
        "Reflect": f"{Color['yellow']}Reflect{Color['reset']}",
        "Absorb": f"{Color['blue']}Absorb{Color['reset']}"
    }
}

replacements = {
    "Ruin Fountain": "yellow",
    "Ultimate Meter": "magenta",
    "Speed Meter": "yellow",
    "Buddy Meter": "cyan",
    "Player": "blue",
    "Players": "blue",
    "Enemy": "red",
    "Enemies": "red",
    "Boss": "red",
    "Buddy": "cyan",
    "Buddies": "cyan",
    "Attack": "cyan",
    "Talent": "yellow",
    "Theme": "yellow",
    "Health": "red",
    "Mana": "blue",
    "Strength": "cyan",
    "Magic": "cyan",
    "Defense": "cyan",
    "Resistance": "cyan",
    "Luck": "yellow",
    "Hit": "yellow",
    "Critical": "yellow",
    "Speed": "yellow",
    "Sanity": "blue",
    "Positive": "yellow",
    "Negative": "red",
    "Status": "green",
}

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def colorize(match, statusClass):
    word = match.group(0)
    status = statusClass.allStatuses.get(word)
    
    if status is None:
        return word
    
    align_colors = {
        "Positive": "green",
        "Negative": "red",
        "Neutral": "yellow",
    }
    color_key = align_colors.get(status.align, "white")
    
    prefix = match.string[:match.start()]
    
    last_color_key = None
    last_pos = -1
    for key, code in Color.items():
        if key == "reset":
            continue
        pos = prefix.rfind(code)
        if pos > last_pos:
            last_pos = pos
            last_color_key = key
    
    reset_pos = prefix.rfind(Color["reset"])
    
    restore_color = Color[last_color_key] if last_pos > reset_pos else ""
    
    return f"{Color[color_key] + Color['line']}{word}{Color['reset']}{restore_color}"

def colorizeReplacement(match, replacements):
    word = match.group(0)
    color_name = replacements.get(word)
    
    if color_name is None:
        return word
    
    prefix = match.string[:match.start()]
    
    last_color_key = None
    last_pos = -1
    for key, code in Color.items():
        if key == "reset":
            continue
        pos = prefix.rfind(code)
        if pos > last_pos:
            last_pos = pos
            last_color_key = key
    
    reset_pos = prefix.rfind(Color["reset"])
    
    restore_color = Color[last_color_key] if last_pos > reset_pos else ""
    
    return f"{Color[color_name]}{word}{Color['reset']}{restore_color}"
    
def line(line_type ):
    if line_type  == "basic":
        print("<-~->")
    
    elif line_type  == "basicOther":
        print("<~=--=~>")
    
    elif line_type == "battle":
        print(f"x< {Color['red']}~-X-~{Color['reset']} >x")
    
    elif line_type == "dialogue":
        print(f"{Color['magenta']}?{Color['reset']}~!{Color['magenta']}-~-{Color['reset']}!~{Color['magenta']}?{Color['reset']}")

    elif line_type == "chrMain":
        print(f"{Color['cyan']}&~{Color['reset']}--{Color['green']}~<{Color['reset']}")

    elif line_type == "chrOther":
        print(f"{Color['green']}>~{Color['reset']}--{Color['cyan']}~>{Color['reset']}")

    elif line_type == "ssLine":
        print(f"+{Color['magenta']}~-<{Color['reset']}=-={Color['magenta']}>-~{Color['reset']}+")

    elif line_type == "ssLineOther":
        print(f"+{Color['cyan']}~-<{Color['reset']}=-={Color['cyan']}>-~{Color['reset']}+")
    
    elif line_type == "buddy":
        print(f"!{Color['cyan']}-<{Color['red']}= ={Color['cyan']}>-~{Color['reset']}!")

    elif line_type == "buddyOther":
        print(f"#{Color['red']}~ <{Color['cyan']}=-={Color['red']}> ~{Color['reset']}#")

    elif line_type == "items":
        print(f"{Color['red']}Z~z{Color['reset']}~={Color['cyan']}-~~-{Color['reset']}=~{Color['red']}z~Z{Color['reset']}")

    elif line_type == "analyze":
        print(f"{Color['yellow']}##-{Color['reset']}--~{Color['yellow']}~=~{Color['reset']}~--{Color['yellow']}-##{Color['reset']}")

    elif line_type == "shop":
        print(f"{Color['green']}$~-~{Color['yellow']}#~#{Color['green']}~-~${Color['reset']}") 

    elif line_type == "shopTrain":
        print(f"{Color['red']}$~-~{Color['yellow']}-!~!-{Color['red']}~-~${Color['reset']}") 
    
    elif line_type == "train":
        print(f"{Color['red']}!Xx{Color['yellow']}X!~~-~~!X{Color['red']}xX!{Color['reset']}")

    elif line_type == "trainReward":
        print(f"{Color['green']}!Xx{Color['yellow']}X!~~-~~!X{Color['green']}xX!{Color['reset']}")

    elif line_type == "trainEvent":
        print(f"{Color['magenta']}!Xx{Color['yellow']}X!~~-~~!X{Color['magenta']}xX!{Color['reset']}")
        
    elif line_type == "statModifier":
        print(f"<{Color['yellow']}~%~{Color['cyan']}+=+{Color['cyan']}~%~{Color['reset']}>")

def dialogue(speaker, text, title=None):
    print(f"{Color['yellow']}{speaker}{Color['reset']}{(', ' + title if title != None else '')}")
    line("dialogue")

    print(text)
    line("dialogue")

def basePath():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def startBattleLog(player, enemy, folderName="battleLogs", sim=False):
    global battleLogFile, _simBattleCounter

    base_dir = basePath()

    if sim:
        folder = os.path.join(base_dir, "utils", "sims")
    else:
        folder = os.path.join(base_dir, folderName)

    os.makedirs(folder, exist_ok=True)
    if not sim:
        limitBattleLogs(maxBattleLogs - 1)

    now = datetime.now()
    safe_player = player.name.replace(" ", "_")
    safe_enemy = enemy.name.replace(" ", "_").replace(",", "").replace(":", "")
    prefix = "" if sim else "rfb_"

    if sim:
        _simBattleCounter += 1
        suffix = f"{_simBattleCounter:06d}"
    else:
        suffix = now.strftime("%d-%H-%M-%S")

    battleLogFile = os.path.join(folder, f"{prefix}{safe_player}_vs_{safe_enemy}_{suffix}.txt")

    with open(battleLogFile, "w", encoding="utf-8") as file:
        file.write(f"{player.name} vs {enemy.name}\n")
        file.write(f"Started: {now.strftime('%d/%H-%M-%S')}\n")
        file.write("=" * 40 + "\n\n")

    with open(battleLogFile, "w", encoding="utf-8") as file:
        file.write(f"{player.name} vs {enemy.name}\n")
        file.write(f"Started: {now.strftime('%d/%H-%M-%S')}\n")
        file.write("=" * 40 + "\n\n")
        
def stripColor(text):
    for code in Color.values():
        text = text.replace(code, "")
    return text

def battleLog(text):
    global battleLogFile

    if not battleLogFile:
        return

    try:
        with open(battleLogFile, "a", encoding="utf-8") as file:
            file.write(stripColor(text) + "\n")
    except (PermissionError, OSError):
        pass

def say(text):
    print(text)
    battleLog(text)

def flushInput():
    if os.name == 'nt':
        import msvcrt
        while msvcrt.kbhit(): msvcrt.getch()

def cleanBattleLogs():    
    base_dir = basePath()
    folder = os.path.join(base_dir, "battleLogs")
    
    if not os.path.exists(folder):
        return
    
    for filename in os.listdir(folder):
        if not filename.endswith(".txt"):
            continue
        
        path = os.path.join(folder, filename)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        
        if "Player Won!" not in content and "Enemy Won!" not in content and "Player Escaped!" not in content:
            os.remove(path)

def limitBattleLogs(maxLogs=maxBattleLogs, folderName="battleLogs"):
    base_dir = basePath()
    folder = os.path.join(base_dir, folderName)

    if not os.path.exists(folder):
        return

    logs = [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.startswith("rfb") and f.endswith(".txt")
    ]

    if len(logs) <= maxLogs:
        return

    logs.sort(key=os.path.getmtime)
    for path in logs[:len(logs) - maxLogs]:
        try:
            os.remove(path)
        except OSError:
            pass