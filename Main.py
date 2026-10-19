from Details import *
print(f"Made By {creator}!")
print(f"Playing Version {gameVersion} of {gameName}")
print("Version 3.14+ of Python Needed")
input("!>")

print(f"Loading {gameName}...")
from gameData.Data import *

def save(player, current):
    player.savedMaps[player.location] = current
    savedStats = {
        "name": player.name,
        "playerClass": player.playerClass,
        "level": player.level,
        "levelGoal": player.levelGoal,
        "levelValue": player.levelValue,
        "skills": [skill.toDict() for skill in player.skills],
        "reserveSkills": [skill.toDict() for skill in player.reserveSkills],
        "sigils": [sigil.toDict() for sigil in player.sigils],
        "reserveSigils": [sigil.toDict() for sigil in player.reserveSigils],
        "buddy": player.buddy.toDict() if player.buddy else None,
        "reserveBuddies": [buddy.toDict() for buddy in player.reserveBuddies],
        "items": [item.toDict() for item in player.items],
        "itemStorage": [item.toDict() for item in player.itemStorage],
        "health": player.health,
        "maxHealth": player.maxHealth,
        "mana": player.mana,
        "maxMana": player.maxMana,
        "strength": player.strength,
        "magic": player.magic,
        "defense": player.defense,
        "resistance": player.resistance,
        "luck": player.luck,
        "hit": player.hit,
        "speed": player.speed,
        "baseMaxHealth": player.baseMaxHealth,
        "baseMaxMana": player.baseMaxMana,
        "baseStrength": player.baseStrength,
        "baseMagic": player.baseMagic,
        "baseDefense": player.baseDefense,
        "baseResistance": player.baseResistance,
        "baseLuck": player.baseLuck,
        "baseHit": player.baseHit,
        "baseSpeed": player.baseSpeed,
        "sigillessMaxHealth": player.sigillessMaxHealth,
        "sigillessMaxMana": player.sigillessMaxMana,
        "sigillessStrength": player.sigillessStrength,
        "sigillessMagic": player.sigillessMagic,
        "sigillessDefense": player.sigillessDefense,
        "sigillessResistance": player.sigillessResistance,
        "sigillessLuck": player.sigillessLuck,
        "sigillessHit": player.sigillessHit,
        "sigillessSpeed": player.sigillessSpeed,
        "coins": player.coins,
        "gamePoints": player.gamePoints,
        "utl": player.utl,
        "vit": player.vit,
        "bdy": player.bdy,
        "modifiers": player.modifiers,
        "x": player.x,
        "y": player.y,
        "location": player.location,
        "savedMaps": {name: mapObj.toDict() for name, mapObj in player.savedMaps.items()},
        "builds": player.builds,
        "travelLog": player.travelLog
    }

    saveFolder = os.path.join(basePath(), "save")
    os.makedirs(saveFolder, exist_ok=True)

    # Search For Existing Save With Characters Name
    duplicateFile = None
    for fileName in os.listdir(saveFolder):
        if fileName.startswith("rfs") and fileName.endswith(".json"):
            filePath = os.path.join(saveFolder, fileName)
            try:
                with open(filePath, "r") as file:
                    data = json.load(file)
                    if data.get("name") == player.name and data.get("playerClass") == player.playerClass:
                        duplicateFile = filePath
                        break
            except json.JSONDecodeError:
                continue
    
    if duplicateFile:
        saveFile = duplicateFile
        try:
            with open(duplicateFile, "r") as f:
                existingDate = json.load(f).get("dateCreated")
        except:
            existingDate = None
    else:
        usedNumbers = []
        for fileName in os.listdir(saveFolder):
            if fileName.startswith("rfs") and fileName.endswith(".json"):
                try:
                    usedNumbers.append(int(fileName[3:-5]))
                except ValueError:
                    pass
        saveNumber = 1000
        while saveNumber in usedNumbers:
            saveNumber += 1
        saveFile = os.path.join(saveFolder, f"rfs{saveNumber}.json")
        existingDate = None

    savedStats["dateCreated"] = existingDate or datetime.now().strftime("%Y-%m-%d")

    with open(saveFile, "w") as file:
        json.dump(savedStats, file, indent=4)

    clear()
    cleanBattleLogs()
    limitBattleLogs()

    line("basic")
    print(f"{Color['yellow']}Saved!{Color['reset']}")
    line("basic")
    input("?>")

def load():
    loop = True
    while loop:
        folderPath = os.path.join(basePath(), "save")
        os.makedirs(folderPath, exist_ok=True)
        saveFiles = [f for f in os.listdir(folderPath) if f.startswith("rfs") and f.endswith(".json")]

        if not saveFiles:
            clear()
            print(f"{Color['red']}No Save Files!{Color['reset']}")
            line("basicOther")
            input("?>")
            return None

        # Display Saves (Skips Corrupted Ones)
        validSaves = []
        clear()
        print(f"{Color['green']}Save Files{Color['reset']}")
        line("basicOther")

        for file in saveFiles:
            filePath = os.path.join(folderPath, file)
            try:
                with open(filePath, "r") as f:
                    data = json.load(f)
                number = file[3:-5]
                validSaves.append((number, filePath))
                name = data["name"]
                playerClass = data["playerClass"]
                level = data["level"]
                dateCreated = data.get("dateCreated", "Unknown")
                print(f"rfs{Color['yellow']}{number} | {name} ({playerClass}, Level {level}){Color['reset']} | Date Created: {dateCreated}")
                line("basic")
            except json.JSONDecodeError:
                print(f"{Color['red']}Corrupted: {file}!{Color['reset']}")
                line("basic")

        print(f"0. {Color['green']}Back{Color['reset']} | 1. {Color['red']}Delete [####]{Color['reset']}")
        line("basicOther")

        choice = input("->")

        if choice == "0":
            return None

        # Delete save
        if "1" in choice and next((f for n, f in validSaves if str(n) in choice), None) and len(choice) == 5:
            selected = next((f for n, f in validSaves if str(n) in choice), None)
            file = os.path.join(folderPath, selected)

            while True:
                choice = input("Are You Sure? 1. Yes | 2. No !?>")
                if choice == "1":
                    os.remove(file)
                    return
                elif choice == "2":
                    break

        # Find chosen save
        selected = next((f for n, f in validSaves if n == choice), None)

        if selected:
            try:
                with open(selected, "r") as file:
                    data = json.load(file)
            except json.JSONDecodeError:
                print(f"{Color['red']}Save file corrupted: {selected}{Color['reset']}")
                input("?>")
                return None

            # Create Empty Player
            player = Player(None, None, None, None, None, None, None, None, None, None, None, None)

            # Stats, Skills, Level, Coins, Etc
            for key, value in data.items():
                setattr(player, key, value)
                
            if getattr(player, "sigillessMaxHealth", None) is None:
                player.sigillessMaxHealth = player.maxHealth
                player.baseMaxHealth = player.maxHealth
                
            if getattr(player, "sigillessMaxMana", None) is None:
                player.sigillessMaxMana = player.maxMana
                player.baseMaxMana = player.maxMana

            if "savedMaps" in data:
                player.savedMaps = {name: Map.fromDict(mapData) for name, mapData in data["savedMaps"].items()}
            else:
                player.savedMaps = {player.location: Map.fromDict(data["map"])}

            # Rebuild Skills & Sigils & Items
            if "skills" in data:
                player.skills = [Skill.fromDict(s) for s in data["skills"]]
                player.reserveSkills = [Skill.fromDict(s) for s in data["reserveSkills"]]
            
            if "sigils" in data:
                player.sigils = [Sigil.fromDict(s) for s in data["sigils"]]
                player.reserveSigils = [Sigil.fromDict(s) for s in data["reserveSigils"]]
            
            if "items" in data:
                player.items = [Item.fromDict(i) for i in data["items"]]

            if "itemStorage" in data:
                player.itemStorage = [Item.fromDict(i) for i in data["itemStorage"]]
                
            if "buddy" in data:
                player.buddy = Buddy.fromDict(data["buddy"]) if data["buddy"] else None
                player.reserveBuddies = [Buddy.fromDict(b) for b in data["reserveBuddies"]]
                              
            return player
        
        else:
            print(f"{Color['red']}Invalid choice. Try again.{Color['reset']}")
            input("?>")

def battleLogDisplay():
    clear()
    folderPath = os.path.join(basePath(), "battleLogs")
    os.makedirs(folderPath, exist_ok=True)
    battleLogs = [f for f in os.listdir(folderPath) if f.startswith("rfb") and f.endswith(".txt")]

    if not battleLogs:
        print(f"{Color['red']}No Battle Logs!{Color['reset']}")
        line("basicOther")
        input("?>")
        return None
    
    while True:
        clear()
        
        print("Battle Logs")
        line("basic")
        
        files = []
        i = 1
        for file in battleLogs:
            files.append([i, file])
            filePath = os.path.join(folderPath, file)
            print(f"{i}. {Color['red']}{file}{Color['reset']}")
            line("basic")
            i += 1
        
        print(f"0. {Color['red']}Back{Color['reset']}")
        line("basicOther")
        
        choice = input("->")
        
        if choice == "0":
            return None

        if choice == "" or not choice.isdigit():
            continue
        
        if choice and choice.isdigit():
            choice = int(choice)
            if 1 <= choice <= len(files):
                selected = next((f for n, f in files if n == choice), None)
                if selected:
                    filePath = os.path.join(folderPath, selected)
                    with open(filePath, "r", encoding="utf-8") as f:
                        data = f.read()
                    clear()
                    print(data)
                    input("?>")

def levelUp(player):
    clear()
    
    player.level += 1
    player.levelValue -= player.levelGoal
    player.levelGoal = round(player.levelGoal * 1.4)

    # Store And Unequip Sigils
    equipped = player.sigils[:]
    for sigil in equipped:
        sigil.unequipSigil(player)

    print(f"{Color['green']}{player.name} Leveled Up!{Color['reset']}")
    line("chrMain")

    for stat, amount in growthTables[player.playerClass].items():
        oldValue = getattr(player, stat)
        setattr(player, stat, getattr(player, stat) + amount)
        newValue = getattr(player, stat)
        if stat not in ("maxHealth", "maxMana"):
            setattr(player, f"base{stat.capitalize()}", getattr(player, f"base{stat.capitalize()}") + amount)
            setattr(player, f"sigilless{stat.capitalize()}", getattr(player, f"sigilless{stat.capitalize()}") + amount)
        
        elif stat == "maxHealth":
            setattr(player, "baseMaxHealth", getattr(player, "baseMaxHealth") + amount)
            setattr(player, "sigillessMaxHealth", getattr(player, "sigillessMaxHealth") + amount)
        
        elif stat == "maxMana":
            setattr(player, "baseMaxMana", getattr(player, "baseMaxMana") + amount)
            setattr(player, "sigillessMaxMana", getattr(player, "sigillessMaxMana") + amount)

        if stat == "maxHealth":
            stat = "Max Health"
        elif stat == "maxMana":
            stat = "Max Mana"
        print(f"{stat.capitalize()}: {Color['cyan']}{oldValue}{Color['reset']} -> {((Color['cyan'] if oldValue == newValue else Color['green']))}{newValue}{Color['reset']}")
    player.health = player.maxHealth
    player.mana = player.maxMana
    line("chrMain")

    # Reequip The Sigils
    for sigil in equipped:
        sigil.equipSigil(player)

    input("?>")

def mainMenu():
    while True:
        clear()
        print(f"{Color['yellow']}{gameName}{Color['reset']} | By {Color['cyan']}eq.official (Instagram/Discord){Color['reset']}")
        line("basicOther")

        print(f"1. {Color['green']}New Game{Color['reset']}",
              f"2. {Color['yellow']}Load Game{Color['reset']}",
              f"3. {Color['magenta']}Battle Logs{Color['reset']}",
              f"4. {Color['red']}Quit{Color['reset']}")
        line("basicOther")
        
        choice = input("->")
        # New Character Creation
        if choice == "1":
            clear()
            dialogue("???", "Welcome to the world of Magnita.\nYour physical container was destroyed long ago, spirit.\nLet me help you.", "the Formless Voice")
            input("?>")

            # Name Section
            clear()
            dialogue("???", "What was your name, spirit?", "the Formless Voice")

            print(f"{Color['yellow']}No Special Characters{Color['reset']}\n"
                  f"{Color['yellow']}No Numbers{Color['reset']}\n"
                  f"{Color['yellow']}Max Of 12 Characters{Color['reset']}")
            line("basicOther")

            name = "1"
            while not (name.isalpha() and len(name) <= 12):
                name = input("->")
            name = name.capitalize()

            # Class Section
            page = 1
            pageLimit = 3
            classLoop = True
            while classLoop:
                clear()
                dialogue("???", "You were a warrior of great renown.\nWhat type were you?", "the Formless Voice")

                if page == 1:
                    print(f"1. {Color['yellow']}I was a Lancer, tough and patient.{Color['reset']}\n"
                        f"2. {Color['yellow']}I was a Magi, obsessed with the otherworldly.{Color['reset']}\n"
                        f"3. {Color['yellow']}I was a Ferkin, raised with the beast.{Color['reset']}\n"
                        f"4. {Color['yellow']}I was a Accursed, shunned by the world for my foulness.{Color['reset']}")
                elif page == 2:
                    print(f"1. {Color['yellow']}I was a Monk, aiming for peace in violence.{Color['reset']}\n"
                    f"2. {Color['yellow']}I was Forlorn, the last of many battles.{Color['reset']}\n"
                    f"3. {Color['yellow']}I was a Scout, running the forest freely.{Color['reset']}\n"
                    f"4. {Color['yellow']}I was an Equinox, merger of conflicting emotions.{Color['reset']}")
                elif page == 3:
                    print(f"1. {Color['yellow']}I was a Cleric, forced to violence.{Color['reset']}\n"
                          f"2. {Color['yellow']}I was a Daredevil, chasing thrills.{Color['reset']}\n"
                          f"3. {Color['yellow']}I was a Tamer, linked to my pals.{Color['reset']}\n"
                          f"4. {Color['yellow']}I was a Thief, my hands were real dirty.{Color['reset']}")
                print("5. Next Page")
                print("6. Previous Page")
                line("basicOther")
                
                playerClass = None
                playerClass = input("->")

                if playerClass == "5":
                    page += 1
                elif playerClass == "6":
                    page -= 1
                
                if page <= 0:
                    page = pageLimit
                
                elif page > pageLimit:
                    page = 1
                
                if playerClass in ["1", "2", "3", "4"]:
                    classLoop = False

                if playerClass == "devnobody":
                    classLoop = "nobody"
                    break
                    
            if not classLoop == "nobody":
                classMatch = {
                    1: {"1": copy.deepcopy(class_lancer),
                        "2": copy.deepcopy(class_magi),
                        "3": copy.deepcopy(class_ferkin),
                        "4": copy.deepcopy(class_accursed)
                    },

                    2: {"1": copy.deepcopy(class_monk),
                        "2": copy.deepcopy(class_forlorn),
                        "3": copy.deepcopy(class_scout),
                        "4": copy.deepcopy(class_equinox)
                    },

                    3: {"1": copy.deepcopy(class_cleric),
                        "2": copy.deepcopy(class_daredevil),
                        "3": copy.deepcopy(class_tamer),
                        "4": copy.deepcopy(class_thief),
                    }
                }
                player = classMatch[page][playerClass]
                player.name = name
            
            else:
                player = class_nobody
                player.name = name

            clear()
            dialogue("Cogito", f"{player.name} the {player.playerClass}... this will be your new container, the new you.\nNow, spirit, leave my presence with my only gift towards you, my name- Cogito.", "the Formless Voice")
            input("?>")
            
            player.location = "Start Zone"
            return player
                    
        # Load Old Character From saves Folder
        elif choice == "2":
            player = load()

            if player:
                return player

        # Displayher Battle Logs
        elif choice == "3":
            battleLogDisplay()

        elif choice == "4":
            clear()
            print(f"{Color['red']}See you next time!{Color['reset']}")
            line("basicOther")
            
            input("?>")
            quit()

def characterScreen(player, map_):
    while True:
        clear()
        print(f"{Color['yellow']}Character Details{Color['reset']}")
        line("chrMain")

        # Player Stats
        meter = ""
        maxBars = 5
        barSize = player.levelGoal / maxBars
        for i in range(maxBars):
            threshold = (i + 1) * barSize
            if player.levelValue > threshold:
                meter += f"{Color['yellow']}▮{Color['reset']}"
            else:
                meter += f"{Color['yellow']}▯{Color['reset']}"

        print(f"{player.name} | {player.playerClass} | {player.level}/20: {meter}\n"
              f"Health: {Color['red']}{player.health}/{player.maxHealth}{Color['reset']} | Mana: {Color['blue']}{player.mana}/{player.maxMana}{Color['reset']}\n"
              f"Coins: {Color['yellow']}{player.coins}{Color['reset']} | Game Points: {Color['cyan']}{player.gamePoints}{Color['reset']}")
        line("chrOther")
        print(f"Strength/Base: {Color['cyan']}{player.strength}/{player.sigillessStrength}{Color['reset']} | Magic/Base: {Color['cyan']}{player.magic}/{player.sigillessMagic}{Color['reset']}\n"
              f"Defense/Base: {Color['cyan']}{player.defense}/{player.sigillessDefense}{Color['reset']} | Resistance/Base: {Color['cyan']}{player.resistance}/{player.sigillessResistance}{Color['reset']}\n"
              f"Luck/Base: {Color['yellow']}{player.luck}/{player.sigillessLuck}{Color['reset']} | Hit/Base: {Color['yellow']}{player.hit}/{player.sigillessHit}{Color['reset']} | Speed/Base: {Color['yellow']}{player.speed}/{player.sigillessSpeed}{Color['reset']}")
        line("chrOther")

        # Active Skill Set
        print(f"Equipped Skills: {Color['cyan']}{len(player.skills)}/6{Color['reset']} | Reserve Skills: {Color['magenta']}{len(player.reserveSkills)}{Color['reset']}")
        number = 0
        for skill in player.skills:
            print(f"{number}. {Color['yellow']}{skill.name} | {skill.element.capitalize() if skill.element != None else skill.element } | {skill.cost + round(player.sigillessMaxMana * 0.06) if not 'Passive' in skill.type_ else 'None'}{Color['reset']}")
            number += 1
        line("chrOther")

        # Active Sigil Set
        print(f"Equipped Sigils: {Color['cyan']}{len(player.sigils)}/3{Color['reset']} | Reserve Sigils: {Color['yellow']}{len(player.reserveSigils)}{Color['reset']}")
        number = 0
        for sigil in player.sigils:
            print(f"{number}. {Color['yellow']}{sigil.name} | {sigil.affinity} | {sigil.effect} {Color['reset']}")
            number += 1
        line("chrOther")

        # Active Buddy
        if player.buddy:
            meter = ""
            maxBars = 5
            barSize = player.buddy.levelGoal / maxBars
            for i in range(maxBars):
                threshold = (i + 1) * barSize
                if player.buddy.levelValue > threshold:
                    meter += f"{Color['cyan']}▮{Color['reset']}"
                else:
                    meter += f"{Color['cyan']}▯{Color['reset']}"
            print(f"Equipped Buddy: {Color['cyan']}{player.buddy.name}{Color['reset']}  | {player.buddy.level}/10: {meter}")
            line("chrOther")
            
        # Options
        print(f"1. Change Skills\n"
          f"2. Change Sigils\n"
          f"3. Change Buddy | {Color['green'] + '!' + Color['reset'] if player.buddy or len(player.reserveBuddies) > 0 else Color['red'] + 'X' + Color['reset']}\n"
          f"4. Presets | {Color['green']}{len(player.builds)}{Color['reset']}\n"
          f"5. Items\n"
          f"6. Travel\n"
          f"7. Back")
        line("chrMain")

        choice = input("->")

        if choice == "1":
            pages = []
            currentPage = 0

            while True:
                clear()
                print(f"{Color['magenta']}Current Skills: {Color['cyan']}{len(player.skills)}/6{Color['reset']}")
                line("ssLine")

                # Active Skills
                number = 0
                for skill in player.skills:
                    print(f"{number}. {skill.name}{' | ' + skill.sanLean if "Damage" in skill.type_ else ''}{f' | Element: {(skill.element.capitalize())}' if skill.element != None else ""}{f' | Cost: {skill.cost + round(player.sigillessMaxMana * 0.06)}' if not 'Passive' in skill.type_ else ""}{f' | Hit: {skill.hit}' if skill.hit > 0 else ""}{f' | Critical: {skill.critical}' if skill.critical > 0 else ""}{f' | Action Cooldown: {f'{skill.cooldown}'}' if skill.cooldown > 0 else ''}")
                    text = Color['yellow'] + skill.text + Color['reset']
                    names = sorted(Status.allStatuses.keys(), key=len, reverse=True)
                    pattern = r"\b(" + "|".join(map(re.escape, names)) + r")\b"
                    text = re.sub(pattern, lambda m: colorize(m, Status), text)
                    print(text)
                    
                    shown = set()
                    for status in Status.allStatuses.values():
                        printStatus(status, skill, shown)
                    number += 1
                    if not number == len(player.skills):
                        print("")
                line("ssLineOther")
                print("")

                # Reserve Skills
                # Page Count
                pages = []
                for skill in player.reserveSkills:
                    if not pages or len(pages[-1]) == 5:
                        pages.append([])
                    pages[-1].append(skill)
                
                if pages and currentPage >= len(pages):
                    currentPage = len(pages) - 1
            
                # Display
                if pages:
                    number = 0
                    print(f"{Color['magenta']}Skills | {Color['yellow']}Page: {currentPage + 1}/{len(pages)}{Color['reset']}")
                    line("ssLineOther")
                    
                    for skill in pages[currentPage]:
                        print(f"{number}. {skill.name}{' | ' + skill.sanLean if "Damage" in skill.type_ else ''}{f' | Element: {(skill.element.capitalize())}' if skill.element != None else ""}{f' | Cost: {skill.cost + round(player.sigillessMaxMana * 0.06)}' if not 'Passive' in skill.type_ else ""}{f' | Hit: {skill.hit}' if skill.hit > 0 else ""}{f' | Critical: {skill.critical}' if skill.critical > 0 else ""}{f' | Action Cooldown: {f'{skill.cooldown}'}' if skill.cooldown > 0 else ''}")
                        text = Color['yellow'] + skill.text + Color['reset']
                        names = sorted(Status.allStatuses.keys(), key=len, reverse=True)
                        pattern = r"\b(" + "|".join(map(re.escape, names)) + r")\b"
                        text = re.sub(pattern, lambda m: colorize(m, Status), text)
                        print(text)
                        
                        shown = set()
                        for status in Status.allStatuses.values():
                            printStatus(status, skill, shown)
                        number += 1
                        if not number == len(pages[currentPage]):
                            print("")

                else:
                    line("ssLineOther")
                    print("No Reserve Skills")
                line("ssLineOther")
                
                # Options
                print(f"E + Skill Number (Equip)\n"
                f"R + Skill Number (Remove)\n"
                f"0. Back")
                
                if currentPage + 1 < len(pages): print("1. Next Page")
                if currentPage > 0: print("2. Previous Page")
                line("ssLine")

                skillChoice  = input("->")

                if (skillChoice .startswith("e") or skillChoice .startswith("E")) and pages:
                    if skillChoice [1:].isdigit() and int(skillChoice [1:]) < len(pages[currentPage]) and len(player.skills) < 6:
                        chosenSkill = pages[currentPage][int(skillChoice [1:])]
                        player.reserveSkills.remove(chosenSkill)
                        player.skills.append(chosenSkill)
                    
                    elif len(player.skills) == 6:
                        print(f"{Color['red']}Max Number Of Skills Equipped!{Color['reset']}")
                        line("ssLine")
                        input(">")
                
                elif (skillChoice .startswith("r") or skillChoice .startswith("R")):
                    if skillChoice [1:].isdigit() and int(skillChoice [1:]) < len(player.skills):
                        chosenSkill = player.skills[int(skillChoice [1:])]
                        player.reserveSkills.append(chosenSkill)
                        player.skills.remove(chosenSkill)

                if skillChoice  == "0":
                    break

                elif skillChoice  == "1" and currentPage + 1 < len(pages):
                    currentPage += 1

                elif skillChoice  == "2" and currentPage  > 0:
                    currentPage -= 1

        elif choice == "2":
            pages = []
            currentPage = 0

            while True:
                clear()
                print(f"{Color['magenta']}Current Sigils: {Color['cyan']}{len(player.sigils)}/3{Color['reset']}")
                line("ssLine")

                # Active Sigils
                number = 0
                for sigil in player.sigils:
                    text = Color['yellow'] + sigil.effect + Color['reset']
                    names = sorted(Status.allStatuses.keys(), key=len, reverse=True)
                    pattern = r"\b(" + "|".join(map(re.escape, names)) + r")\b"
                    text = re.sub(pattern, lambda m: colorize(m, Status), text)
                    
                    print(f"{number}. {sigil.name} | {sigil.affinity} | {text}")
                    print(f"{Color['cyan']}{sigil.flavor}{Color['reset']}")
                    shown = set()
                    for status in Status.allStatuses.values():
                        printStatus(status, sigil, shown)
                    number += 1
                    if not number == len(player.sigils):
                        print("")
                line("ssLineOther")
                print("")

                # Reserve Sigils
                # Page Count
                pages = []
                for sigil in player.reserveSigils:
                    if not pages or len(pages[-1]) == 8:
                        pages.append([])
                    pages[-1].append(sigil)
                
                if pages and currentPage >= len(pages):
                    currentPage = len(pages) - 1
            
                # Display
                if pages:
                    number = 0
                    print(f"{Color['magenta']}Sigils | {Color['yellow']}Page: {currentPage + 1}/{len(pages)}{Color['reset']}")
                    line("ssLineOther")

                    for sigil in pages[currentPage]:
                        text = Color['yellow'] + sigil.effect + Color['reset']
                        names = sorted(Status.allStatuses.keys(), key=len, reverse=True)
                        pattern = r"\b(" + "|".join(map(re.escape, names)) + r")\b"
                        text = re.sub(pattern, lambda m: colorize(m, Status), text)
                        
                        print(f"{number}. {sigil.name} | {sigil.affinity} | {text}")
                        print(f"{Color['cyan']}{sigil.flavor}{Color['reset']}")
                        shown = set()
                        for status in Status.allStatuses.values():
                            printStatus(status, sigil, shown)
                        number += 1
                        if not number == len(pages[currentPage]):
                            print("")

                else:
                    line("ssLineOther")
                    print("No Reserve Sigil")
                line("ssLineOther")
                
                # Options
                print(f"E + Sigil Number (Equip)\n"
                f"R + Sigil Number (Remove)\n"
                f"0. Back")
                
                if currentPage + 1 < len(pages): print("1. Next Page")
                if currentPage > 0: print("2. Previous Page")
                line("ssLine")

                sigilChoice  = input("->")

                if (sigilChoice .startswith("e") or sigilChoice .startswith("E")) and pages:
                    if sigilChoice [1:].isdigit() and int(sigilChoice [1:]) < len(pages[currentPage]) and len(player.sigils) < 3:
                        chosenSigil = pages[currentPage][int(sigilChoice [1:])]
                        chosenSigil.equipSigil(player)
                        
                    elif len(player.sigils) == 3:
                        print(f"{Color['red']}Max Number Of Sigils Equipped!{Color['reset']}")
                        line("ssLine")
                        input(">")
                        
                elif sigilChoice .startswith("r") or sigilChoice .startswith("R"):
                    if sigilChoice [1:].isdigit() and int(sigilChoice [1:]) < len(player.sigils):
                        chosenSigil = player.sigils[int(sigilChoice [1:])]
                        chosenSigil.unequipSigil(player)

                if sigilChoice  == "0":
                    break

                elif sigilChoice  == "1" and currentPage + 1 < len(pages):
                    currentPage += 1

                elif sigilChoice  == "2" and currentPage  > 0:
                    currentPage -= 1
        
        elif choice == "3" and (player.buddy or len(player.reserveBuddies) > 0):
            pages = []
            currentPage = 0

            while True:
                clear()
                print(f"{Color['yellow']}Active Buddy{Color['reset']}")
                line("buddy")

                # Active Buddy
                if player.buddy:
                    print(f"{player.buddy.name} {Color['reset']}|{Color['cyan']} {player.buddy.affinity}| Level: {player.buddy.level}")
                    print(f"{Color['cyan']}Attack: {player.buddy.attack} {Color['reset']}|{Color['cyan']} Talent: {player.buddy.talent} {Color['reset']}|{Color['cyan']} Speed: {player.buddy.speed}{Color['reset']}")
                    
                    text = Color['yellow'] + player.buddy.passive.text + Color['reset']
                    names = sorted(Status.allStatuses.keys(), key=len, reverse=True)
                    pattern = r"\b(" + "|".join(map(re.escape, names)) + r")\b"
                    text = re.sub(pattern, lambda m: colorize(m, Status), text)
                    print(f"{player.buddy.passive.name}: {text}")
                    
                    text = Color['yellow'] + player.buddy.skill.text + Color['reset']
                    names = sorted(Status.allStatuses.keys(), key=len, reverse=True)
                    pattern = r"\b(" + "|".join(map(re.escape, names)) + r")\b"
                    text = re.sub(pattern, lambda m: colorize(m, Status), text)
                    print(f"{player.buddy.skill.name}: {text} {f'| {Color['yellow']} Hit: {player.buddy.skill.hit} {Color['reset']} | {Color['yellow']} Critical: {player.buddy.skill.critical}' if 'Damage' in player.buddy.skill.type_ else ''} {Color['reset']}")
                    
                    shown = set()
                    for status in Status.allStatuses.values():
                        printStatus(status, player.buddy.passive, shown)
                    for status in Status.allStatuses.values():
                        printStatus(status, player.buddy.skill, shown)
                else:
                    print("No Buddy Equipped!")
                line("buddyOther")
                print("")

                # Reserve Sigils
                # Page Count
                pages = []
                for buddy in player.reserveBuddies:
                    if not pages or len(pages[-1]) == 3:
                        pages.append([])
                    pages[-1].append(buddy)
                
                if pages and currentPage >= len(pages):
                    currentPage = len(pages) - 1
            
                # Display
                if pages:
                    number = 0
                    print(f"{Color['magenta']}Buddies | {Color['yellow']}Page: {currentPage + 1}/{len(pages)}{Color['reset']}")
                    line("buddyOther")

                    for buddy in pages[currentPage]:
                        print(f"{number}. {buddy.name} {Color['reset']}|{Color['cyan']} {buddy.affinity} | Level: {buddy.level}")
                        print(f"{Color['cyan']}Attack: {buddy.attack} {Color['reset']}|{Color['cyan']} Talent: {buddy.talent} {Color['reset']}|{Color['cyan']} Speed: {buddy.speed}{Color['reset']}")
                        
                        text = Color['yellow'] + buddy.passive.text + Color['reset']
                        names = sorted(Status.allStatuses.keys(), key=len, reverse=True)
                        pattern = r"\b(" + "|".join(map(re.escape, names)) + r")\b"
                        text = re.sub(pattern, lambda m: colorize(m, Status), text)
                        print(f"{buddy.passive.name}: {text}")
                        
                        text = Color['yellow'] + buddy.skill.text + Color['reset']
                        names = sorted(Status.allStatuses.keys(), key=len, reverse=True)
                        pattern = r"\b(" + "|".join(map(re.escape, names)) + r")\b"
                        text = re.sub(pattern, lambda m: colorize(m, Status), text)
                        print(f"{buddy.skill.name}: {text} {f'| {Color['yellow']} Hit: {buddy.skill.hit} {Color['reset']} | {Color['yellow']} Critical: {buddy.skill.critical}' if 'Damage' in buddy.skill.type_ else ''} {Color['reset']}")
                        
                        shown = set()
                        for status in Status.allStatuses.values():
                            printStatus(status, buddy.passive, shown)
                        for status in Status.allStatuses.values():
                            printStatus(status, buddy.skill, shown)
                        number += 1
                        if not number == len(pages[currentPage]):
                            print("")

                else:
                    line("buddyOther")
                    print("No Reserve Buddies")
                line("buddyOther")
                
                # Options
                print(f"E + Buddy Number (Equip)\n"
                f"{Color['red']}Type 'Remove' To Remove Buddy{Color['reset']}\n"
                f"0. Back")
                
                if currentPage + 1 < len(pages): print("1. Next Page")
                if currentPage > 0: print("2. Previous Page")
                line("buddy")

                buddyChoice  = input("->")

                if buddyChoice.startswith("e") or buddyChoice .startswith("E"):
                    if buddyChoice [1:].isdigit() and int(buddyChoice [1:]) < len(pages[currentPage]) and not player.buddy:
                        chosenBuddy = pages[currentPage][int(buddyChoice [1:])]
                        player.buddy = chosenBuddy
                        player.reserveBuddies.remove(chosenBuddy)
                        
                    elif player.buddy:
                        print(f"{Color['red']}Buddy Already Equipped!{Color['reset']}")
                        line("buddy")
                        input(">")
                        
                elif buddyChoice.lower() == "remove":
                    player.reserveBuddies.append(player.buddy)
                    player.buddy = None

                if buddyChoice  == "0":
                    break

                elif buddyChoice  == "1" and currentPage + 1 < len(pages):
                    currentPage += 1

                elif buddyChoice  == "2" and currentPage  > 0:
                    currentPage -= 1

        elif choice == "4":
                     
            while True:
                clear()
                
                print("Presets")
                line("chrMain")
                    
                if len(player.builds) > 0:
                    num = 0
                    for build in player.builds.values():
                        print(f"{num}. {build['name']}")
                        num += 1
                
                else:
                    print("No Presets!")
                line("chrMain")
                
                print("Preset # -> Equip Preset\n"
                      f"d + Preset # -> Delete Preset\n"
                      f"{Color['green']}Type 'Save' To Save Current Build{Color['reset']}\n"
                      f"{Color['red']}Type 'Exit' To Leave{Color['reset']}")
                
                choice = input("->")
                
                if choice.isnumeric() and int(choice) > -1 and int(choice) < len(player.builds):
                    build = list(player.builds.values())[int(choice)]

                    # Error Checks
                    for skill in build["skills"]:
                        if not any(s.name == skill for s in player.skills + player.reserveSkills):
                            print(f"{Color['red']}Missing Preset Skill!{Color['reset']}")
                            print(f"{Color['red']}Deleting Preset!{Color['reset']}")
                            player.builds.pop(list(player.builds.keys())[int(choice)])
                            input("?>")
                            return
                    
                    for sigil in build["sigils"]:
                        if not any(s.name == sigil for s in player.sigils + player.reserveSigils):
                            print(f"{Color['red']}Missing Preset Sigil!{Color['reset']}")
                            print(f"{Color['red']}Deleting Preset!{Color['reset']}")
                            player.builds.pop(list(player.builds.keys())[int(choice)])
                            input("?>")
                            return

                    if build["buddy"] is not None  and not any(build["buddy"] == b.name for b in ([player.buddy] + player.reserveBuddies if player.buddy is not None else player.reserveBuddies)):
                        print(f"{Color['red']}Missing Preset Buddy!{Color['reset']}")
                        print(f"{Color['red']}Deleting Preset!{Color['reset']}")
                        player.builds.pop(list(player.builds.keys())[int(choice)])
                        input("?>")
                        return
                    
                    # Removing
                    for skill in player.skills[:]:
                        player.skills.remove(skill)
                        player.reserveSkills.append(skill)
                    
                    for sigil in player.sigils[:]:
                        player.sigils.remove(sigil)
                        player.reserveSigils.append(sigil)
                                            
                    if player.buddy:
                        player.reserveBuddies.append(player.buddy)
                        player.buddy = None
                    
                    # Equipping
                    for skill in build["skills"]:
                        skill = next(s for s in player.reserveSkills if s.name == skill)
                        player.skills.append(skill)
                        player.reserveSkills.remove(skill)
                        
                        
                    for sigil in build["sigils"]:
                        sigil = next(s for s in player.reserveSigils if s.name == sigil)
                        player.sigils.append(sigil)
                        player.reserveSigils.remove(sigil)
                    
                    if build["buddy"] is not None:
                        bud = next((s for s in player.reserveBuddies if s.name == build["buddy"]), None)
                        player.buddy = bud
                        if bud:
                            player.reserveBuddies.remove(bud)
                    
                    print(f"{Color['green']}Preset Equipped!{Color['reset']}")
                    line("chrMain")
                    
                    input("->")
                    break
                                      
                elif choice.startswith("d") or choice.startswith("D"):
                    choice = choice.replace("d", "")
                    choice = choice.replace("D", "")
                    
                    if choice.isnumeric() and int(choice) > -1 and int(choice) < len(player.builds):
                        player.builds.pop(list(player.builds.keys())[int(choice)])
                        
                        print(f"{Color['red']}Preset Deleted!{Color['reset']}")
                        line("chrMain")
                        
                        input("->")
                
                elif choice.lower() == "save":
                    while True:
                        clear()
                        
                        print(f"{Color['cyan']}Build Name?{Color['reset']}")
                        line("chrMain")                       
                        name = "1"
                        while not name.isalpha():
                            name = input("->")
                        name = name.capitalize()
                        
                        player.builds[name] = {
                            "name": name,
                            "skills": [skill.name for skill in player.skills], 
                            "sigils": [sigil.name for sigil in player.sigils], 
                            "buddy": player.buddy.name if player.buddy else None
                        }
                        
                        clear()
                        print(f"{Color['green']}Preset Created{Color['reset']}")
                        line("chrMain")
                        
                        input("?>")
                        break
                
                if choice.lower() == "exit":
                    break
                      
        elif choice == "5":
            page = []
            currentPage = 0

            while True:
                clear()

                pages = []
                for item in player.items:
                    if not pages or len(pages[-1]) == 5:
                        pages.append([])
                    pages[-1].append(item)

                if pages and currentPage >= len(pages):
                    currentPage = len(pages) - 1

                if pages:
                    number = 0
                    print(f"{Color['cyan']}Items | {Color['yellow']}Page: {currentPage + 1}/{len(pages)}{Color['reset']}")
                    line("chrMain")
                    for item in pages[currentPage]:
                        print(f"{number}. {item.name} | {item.playerAmount}/{item.maxAmount} {f'| Hit: {item.hit}' if item.hit > 0 else ''}")
                        text = Color['green'] + item.effect + Color['reset']
                        names = sorted(Status.allStatuses.keys(), key=len, reverse=True)
                        pattern = r"\b(" + "|".join(map(re.escape, names)) + r")\b"
                        text = re.sub(pattern, lambda m: colorize(m, Status), text)
                        print(text)
                        
                        shown = set()
                        for status in Status.allStatuses.values():
                            printStatus(status, item, shown)
                            
                        if "Skill" in item.type_:
                            print(f"Skill Detail: {Color['yellow']}{item.skill.element.capitalize() if item.skill.element != None else item.skill.element } | Cost: {item.skill.cost + round(player.sigillessMaxMana * 0.06)} | Hit: {item.skill.hit} | Crit: {item.skill.critical}{Color['reset']}")
                            print(f"Skill Effect: {Color['cyan']}{item.skill.text}{Color['reset']}")
                        number += 1
                        if number != len(pages[currentPage]):
                            print("")
                else:
                    print("No Items!")
                line("chrMain")

                print(f"U + Item Number (Use)\n"
                        "0. Back")
                if currentPage + 1 < len(pages): print("1. Next Page")
                if currentPage > 0: print("2. Previous Page")
                line("chrMain")

                itemChoice = input("->")

                if itemChoice.startswith("u") or itemChoice.startswith("U"):
                    idx = itemChoice[1:]
                    if pages and idx.isdigit() and int(idx) < len(pages[currentPage]):
                        chosen = pages[currentPage][int(idx)]
                        if "Damage" not in chosen.type_ and "StatusC" not in chosen.type_ and "StatusI" not in chosen.type_ and "Cleanse" not in chosen.type_ and chosen.useType != "Battle":
                            chosen.use(player, None)
                        else:
                            print("Cannot Use This Item Out Of Battle!")
                        input("?>")

                elif itemChoice == "0":
                    break

                elif itemChoice == "1" and currentPage + 1 < len(pages):
                    currentPage += 1

                elif itemChoice == "2" and currentPage > 0:
                    currentPage -= 1

        elif choice == "6":
            while True:
                if len(player.travelLog) > 0:
                    clear()
                    print("Fast Travel")
                    line("chrMain")

                    number = 0
                    for location in player.travelLog:
                        print(f"{number}. {Map.allMaps.get(location).name} | Level Rec: {Map.allMaps.get(location).scaling[0]}-{Map.allMaps.get(location).scaling[1]} Enemies: {len(Map.allMaps.get(location).enemies)}")
                        line("chrOther")
                        number += 1
                    print("")

                    line("chrOther")
                    print(f"{Color['red']}Type Exit To Leave{Color['reset']}")
                    line("chrMain")

                    choice = input("->")

                    if choice in ["Exit", "exit"]:
                        break

                    if choice.isdigit() and int(choice) <= len(player.travelLog) - 1:
                        choice = int(choice)
                        if Map.allMaps.get(player.travelLog[choice]).name == player.location:
                            print(f"Already In {player.location}")
                            input("?>")
                        else:
                            map_.transition(player, player.travelLog[choice], Map.allMaps.get(player.travelLog[choice]).travelCords[0], Map.allMaps.get(player.travelLog[choice]).travelCords[1])
                            return None

                else:
                    print(f"{Color['red']}No Locations To Travel To!{Color['reset']}")
                    input("?>")

        elif choice == "7":
            break

def guide():
    active = True
    currentPage = 0
    while active:
        clear()
        
        pages = []
        for guide in Guide.guides:
            if not pages or len(pages[-1]) >= 10:
                pages.append([])
            pages[-1].append(guide)
        
        if pages and currentPage >= len(pages):
            currentPage = len(pages) - 1
    
        print(f"Current Page: {currentPage}")
        line("dialogue")
        
        if pages:
            number = 1
            for guide in pages[currentPage]:
                print(f"{number}. {guide}")
                number += 1
            line("dialogue")
        
        else:
            return
        
        print()
        line("basic")
        
        print(f"{Color['red']}Type 'Exit' To Leave{Color['reset']}")
        if currentPage < len(pages) - 1: print("Type 'Next' For Next Page")
        if currentPage > 0: print("Type 'Pre' For Previous Page")
        line("basic")
        
        choice = input("?>")
        
        if choice.isnumeric() and int(choice) < 11 and int(choice) > 0:
            clear()
            
            print(pages[currentPage][int(choice) - 1])
            line("dialogue")
            print("")
            
            display = Guide.guides[pages[currentPage][int(choice) - 1]]
            names = sorted(Status.allStatuses.keys(), key=len, reverse=True)
            pattern = r"\b(" + "|".join(map(re.escape, names)) + r")\b"
            display = re.sub(pattern, lambda m: colorize(m, Status), display)
            
            repKeys = sorted(replacements.keys(), key=len, reverse=True)
            repPattern = r"\b(" + "|".join(map(re.escape, repKeys)) + r")\b"
            display = re.sub(repPattern, lambda m: colorizeReplacement(m, replacements), display)
            
            print(display)
            print("")
            line("dialogue")
            input(">")
        
        if choice.lower() == "next" and not currentPage == len(pages) - 1:
            currentPage += 1
        
        elif choice.lower() == "pre" and currentPage > 0:
            currentPage -= 1
        
        elif choice.lower() == "exit":
            break

DEBUG = False
def debug(map_, player):
    global DEBUG, PEACE, CORDS, DRAW, DELETE, GHOST
    
    def debugSelect(pool, label="Results"):
        names = list(pool.keys())
        pages = [names[i:i + 10] for i in range(0, len(names), 10)]
        page = 0

        while True:
            clear()
            print(f"{Color['yellow']}{label} | Page {page + 1}/{len(pages)}{Color['reset']}")
            line("basic")

            for i, name in enumerate(pages[page]):
                print(f"{i}. {name}")
            line("basic")

            print("Number. Select" +
                (" | N. Next Page" if page + 1 < len(pages) else "") +
                (" | P. Previous Page" if page > 0 else "") +
                f" | {Color['red']}Type 'Exit' To Leave{Color['reset']}")

            choice = input("?>")

            if choice.lower() == "exit":
                return None
            elif choice.lower() == "n" and page + 1 < len(pages):
                page += 1
            elif choice.lower() == "p" and page > 0:
                page -= 1
            elif choice.isdigit() and int(choice) < len(pages[page]):
                return pool[pages[page][int(choice)]]
            elif any(choice == s for s in pool.keys()):
                return pool[choice]
    
    while DEBUG:
        clear()
        print("DEBUG MENU:")
        line("basic")

        print("1. Add All Items\n"
            "2. Add Coins\n"
            "3. Add GP\n"
            "4. Add Level Value\n"
            "5. Fight Enemy\n"
            "6. Full Heal\n"
            "7. Give Skill\n"
            "8. Travel\n"
            "9. Back")
        line("basicOther")
        
        print(f"{Color['red']}--dbug - Open Debug Menu\n"
              "cordsbug - Show Cordinates\n"
              "drawbug - Paint Tiles\n"
              "delbug - Delete Tiles\n"
              "ghostbug - Walk Through Walls\n"
              "offbug - Turn Of All Debug Variables\n"
              f"offlog/onlog - Toggle Battle Logging{Color['reset']}")
        line("basic")

        choice = input("~>")

        if choice == "1":
            for item in Item.allItems:
                if "Skill" in Item.allItems[item].type_: continue
                Item.allItems[item].tracker(99, "Add", player)
            
            for sigil in Sigil.allSigils.values():
                if not any(s.name == sigil.name for s in (player.sigils + player.reserveSigils)):
                    player.reserveSigils.append(copy.copy(sigil))

        elif choice == "2":
            amount = input("+>")
            player.coins += int(amount)

        elif choice == "3":
            amount = input("+>")
            player.gamePoints += int(amount)

        elif choice == "4":
            amount = input("+>")
            player.levelValue += int(amount)
            if player.level > 20:
                player.level = 20

        elif choice == "5":
            chosen = debugSelect(Enemy.allEnemies, "Enemies")
            if chosen:
                map_.bossEncounter(player, copy.deepcopy(chosen))
                player.health = player.maxHealth
                player.mana = player.maxMana
        
        elif choice == "6":
            player.health = player.maxHealth
            player.mana = player.maxMana

        elif choice == "7":
            chosen = debugSelect(PlayerSkill.allSkills, "Skills")
            if chosen:
                player.reserveSkills.append(copy.deepcopy(chosen))
                print(f"{Color['green']}Learned {chosen.name}!{Color['reset']}")
                input("?>")

        elif choice == "8":
            location = input("Location>")
            x = int(input("X>"))
            y = int(input("Y>"))
            
            if location in Map.allMaps:
                targetMap = Map.allMaps[location]
                player.savedMaps[player.location] = map_
                player.location = targetMap.name
                
                if (x > 0 and x <= targetMap.maxX) and (y > 0 and y <= targetMap.maxY):
                    player.x = x
                    player.y = y
                
                return None
            else:
                print(f"{Color['red']}Map Does Not Exist!{Color['reset']}")
                input("?>")

        elif choice == "9":
            DEBUG = False

        elif choice == "cordsbug":
            CORDS = True
        
        elif choice == "drawbug":
            if DRAW:
                DRAW = False
                continue
            DRAW = True
            DELETE = False
            
        elif choice == "delbug":
            if DELETE:
                DELETE = False
                continue
            DELETE = True
            DRAW = False
            
        elif choice == "ghostbug":
            if GHOST:
                GHOST = False
                continue
            GHOST = True
    
        elif choice == "offbug":
            CORDS = False
            DRAW = False
            DELETE = False
            GHOST = False
        
        elif choice == "offlog":
            player.logs = False
        
        elif choice == "onlog":
            player.logs = True
            
STEPS = 0
PEACESTEPS = 2
PEACE = False
CORDS = False
DRAW = False
DELETE = False
GHOST = False

# Raid Things
raidItemPool = [
    # This should be rare items, with 3 unique raid items.
    # Rarer items should be weighted based on Luck.
    # (item, random_min, random_max)
    (item_full_power, 1, 2),
    (item_phoenix_feather, 1, 1),
    (item_phoenix_elixer, 1, 2),
    (item_elixer, 1, 3),
    (item_mini_elixer, 2, 4),
    (item_boulder_sling, 2, 4),
    (item_pocket_watch, 2, 5),
    (item_buddy_medium, 4, 8),
]

raidSpecialPool = [
    # This should be skills, sigils, and buddies on the level of extreme zone.
    # If the player already has the reward, they gain GP instead. Gives more excentitive to redue raids for what you want.
    # Rarer rewards (Raid specific) should be weighted based on Luck.
]

def run(map_, player):
    global outerLoop, innerLoop, STEPS, PEACESTEPS, DEBUG, PEACE, CORDS, DRAW, DELETE, GHOST
    clear()

    # Tracks Maps Player Hsa Been To
    if player.location not in player.travelLog: player.travelLog.append(player.location)

    # Step Tracker And Stat Refresh
    STEPS += 1
    if STEPS >= 3:
        for stat in ["maxHealth", "maxMana", "strength", "magic", "defense", "resistance", "luck", "hit", "speed"]:
            if stat == "maxHealth": setattr(player, stat, getattr(player, f"sigillessMaxHealth")); continue
            if stat == "maxMana": setattr(player, stat, getattr(player, f"sigillessMaxMana")); continue       
            setattr(player, stat, getattr(player, f"sigilless{stat.capitalize()}"))
        for equipped in player.sigils:
            for stat, amount in equipped.statChange: setattr(player, stat, getattr(player, stat) + amount)
        for stat in ["maxHealth", "maxMana", "strength", "magic", "defense", "resistance", "luck", "hit", "speed"]:
            if stat != "speed": setattr(player, stat, max(1, getattr(player, stat)))
            else: setattr(player, stat, max(5, getattr(player, stat)))
        STEPS = 0

    # Enemy Encounters
    if PEACESTEPS > 0:
        PEACESTEPS -= 1
    if not PEACE and PEACESTEPS <= 0:
        result = map_.enemyEncounter(player)
        if result == "Loss":
            innerLoop = False
            return
        
        elif result == "Escape":
            PEACE = True
            PEACESTEPS = 3

    # Level Up
    if player.levelValue >= player.levelGoal and player.level < 20:
        while player.levelValue >= player.levelGoal and not player.level >= 20:
            levelUp(player)
            clear()
    
    # Buddy Level Up
    if player.buddy and player.buddy.levelValue >= player.buddy.levelGoal and player.buddy.level < 10:
        while player.buddy.levelValue >= player.buddy.levelGoal and not player.buddy.level >= 10:
            player.buddy.levelUp()
            clear()
        
    # Information Display
    print(f"{Color['yellow']}{map_.name}{Color['reset']}")
    print(f"{player.name} the {player.playerClass}")
    line("basicOther")
    
    print(f"Health: {Color['red']}{player.health}/{player.maxHealth}{Color['reset']} | Mana: {Color['blue']}{player.mana}/{player.maxMana}{Color['reset']}")
    print(f"Strength: {Color['cyan']}{player.strength}{Color['reset']} | Magic: {Color['cyan']}{player.magic}{Color['reset']}")
    print(f"Defense: {Color['cyan']}{player.defense}{Color['reset']} | Resistance: {Color['cyan']}{player.resistance}{Color['reset']}")
    print(f"Luck: {Color['yellow']}{player.luck}{Color['reset']} | Hit: {Color['yellow']}{player.hit}{Color['reset']} | Speed: {Color['yellow']}{player.speed}{Color['reset']}")
    line("basic")

    display = map_.display(player)
    for row in display:
        print(row)
    line("basic")
    if CORDS:
        print(f"X: {player.x} | Y: {player.y}")
        line("basicOther")
        print("")
    
    # Movement/Wall Options And Info
    currentTile = map_.tiles.get((player.y, player.x))
    
    if currentTile["wallNorth"]:
        print(f"{Color['cyan']}Wall Ahead!{Color['reset']}")
    if currentTile["wallWest"]:
        print(f"{Color['cyan']}Wall To The Left!{Color['reset']}")
    if currentTile["wallSouth"]:
        print(f"{Color['cyan']}Wall Behind!{Color['reset']}")
    if currentTile["wallEast"]:
        print(f"{Color['cyan']}Wall To The Right!{Color['reset']}")

    # Current Tile Info
    result = map_.tileBehavior(player)
    if result and result == "Win":
        return

    elif result and result == "Loss":
        innerLoop = False
        return

    elif result and result == "Continue":
        previous = currentTile.get("previous")

        if previous == "north":
            player.y -= 1
        elif previous == "south":
            player.y += 1
        elif previous == "west":
            player.x -= 1
        elif previous == "east":
            player.x += 1

        player.x = max(1, min(player.x, map_.maxX))
        player.y = max(1, min(player.y, map_.maxY))
        STEPS = 3
        return
    
    if currentTile["wallNorth"] or currentTile["wallWest"] or currentTile["wallSouth"] or currentTile["wallEast"]:
        line("basicOther")

    if currentTile["type"] == "buddyShop" and player.level < 5:
        print(f"{Color['red']}Level Must Be At 5+ To Enter!{Color['reset']}")
    
    print(f"{Color['yellow']}W.A.S.D{Color['reset']}")

    # Other Options
    print(f"0. Character Info\n"
          f"1. Menu\n"
          f'2. Guide')
    if currentTile["type"] in ["transition", "gate", "gateHaz", "gateNull"]:
        print(f"3. Move To Different Location?")
    if currentTile["type"] == "whirl":
        print(f"3. Enter Whril?")
    if currentTile["type"] == "raid":
        print(f"3. Begin Raid?")
    line("basicOther")
    
    choice = input("->").strip()
    
    # Options Effects
    if choice and choice in "wWaAsSdD":
        PEACE = False
        map_.movement(player, choice, GHOST)
        if DRAW:
            currentTile["type"] = "safe"
            currentTile["hazard"] = None
        elif DELETE:
            currentTile["type"] = "none"
            currentTile["hazard"] = None
    
    elif choice == "0":
        PEACE = True
        PEACESTEPS = 2
        characterScreen(player, map_)

    elif choice == "1":
        PEACE = True
        PEACESTEPS = 2
        clear()
        
        print("Menu")
        line("basic")
        
        print(f"1. {Color['yellow']}Save {Color['reset']}&{Color['red']} Quit{Color['reset']} | 2. {Color['red']}Quit{Color['reset']} | 3. {Color['yellow']}Save{Color['reset']} | 4. Back")
        line("basic")
        
        while True:
            choice = input("?>")
            
            if choice == "1":
                save(player, map_)
                innerLoop = False
                break
            
            elif choice == "2":
                innerLoop = False
                break

            elif choice == "3":
                save(player, map_)
                break
            
            elif choice == "4":
                break
    
    elif choice == "2":
        PEACE = True
        PEACESTEPS = 2
        guide()
    
    elif currentTile["type"] == "transition" and choice == "3":
        PEACE = True
        PEACESTEPS = 1
        map_.transition(player, currentTile["hazard"][0], currentTile["hazard"][1], currentTile["hazard"][2])

    elif currentTile["type"] in ["gate", "gateHaz", "gateNull"] and choice == "3":
        PEACE = True
        PEACESTEPS = 1
        map_.gate(player, currentTile["hazard"][0], currentTile["hazard"][1], currentTile["hazard"][2], currentTile["hazard"][3], currentTile)
    
    elif currentTile["type"] == "whirl" and choice == "3":
        PEACE = True
        PEACESTEPS = 1
        player.x = currentTile['hazard'][0]
        player.y = currentTile["hazard"][1]

    elif currentTile["type"] == "raid" and choice == "3":
        raid = False
        win = False
            
        while True:
            clear()
            print(f"{Color['red']}Begin Raid?{Color['reset']}")
            line("battle")

            options = ""
            if player.level >= 15:
                options += f"1. {Color['green']}Challenge Meliane{Color['reset']} | {Color['yellow']}(Rec: Level 15+){Color['reset']}\n"

            if player.level >= 20:
                options += f"2. {Color['red']}Challenge Hanbo{Color['reset']} | {Color['yellow']}(Rec: Level 20){Color['reset']}\n"

            options += "6. Exit"

            print(options)
            line("battle")

            choice = input("->")
            if choice == "1" and player.level >= 15:
                raidBoss = copy.deepcopy(raid_boss_meliane)
                bossMap = Map.placements(copy.deepcopy(special_melianes_bank), player, [raidBoss], True)
                enemyMap = Map.placements(copy.deepcopy(special_melianes_plain), player, [special_energy_wisp, special_orchid_swan], True)
                addToMaps = [enemyMap, bossMap]

                rewardItem = None # <- Rare Item
                rewardSpecial = None # <- Should be luck based & is Skill, Sigil, or Buddy
                raid = True
                break

            elif choice == "2" and player.level >= 20:
                raidBoss = copy.deepcopy(raid_boss_hanbo)
                bossMap = Map.placements(copy.deepcopy(special_hanbos_temple), player, [raidBoss], True)
                enemyMap = Map.placements(copy.deepcopy(special_hanbos_temple_entrance), player, [special_undead_phoenix, special_pale_clad_soldier], True)
                addToMaps = [enemyMap, bossMap]

                rewardItem = None # <- Rare Item
                rewardSpecial = None # <- Should be luck based & is Skill, Sigil, or Buddy
                raid = True
                break
                
            elif choice == "6":
                break

        if raid:    
            raidPlayer, maps = map_.startRaid(player, normal_raid_maps)
            maps += addToMaps
            
            while True and raidPlayer.progress != 5:
                if raidPlayer.health > 0:
                    raidPlayer.x = maps[raidPlayer.progress].travelCords[1]
                    raidPlayer.y = maps[raidPlayer.progress].travelCords[0]
                    while True:
                        result = raidRun(maps[raidPlayer.progress], raidPlayer, lambda: guide())

                        if result and result == "Win":
                            raidPlayer.progress += 1
                            if raidPlayer.progress == 5:
                                win = True
                                break
                            raidPlayer.x = maps[raidPlayer.progress].travelCords[1]
                            raidPlayer.y = maps[raidPlayer.progress].travelCords[0]

                        elif win or result == "Loss":
                            break

                    if result == "Loss":
                        break
                        # Add Lose Message

            del raidPlayer

        if win:
            pass # <- Reward Givnig Will Go Here

    elif choice == "--dbug":
        DEBUG = True
        PEACE = True
        PEACESTEPS = 5
        debug(map_, player)
    
    else:
        return
    
# Outer Loop
outerLoop = True
while outerLoop:
    cleanBattleLogs()
    limitBattleLogs()
    player = mainMenu()

    # Inner Loop
    innerLoop = True
    while innerLoop:
        cleanBattleLogs()
        limitBattleLogs()
        # Reset Player Stats To Base
        for stat in ["maxHealth", "maxMana", "strength", "magic", "defense", "resistance", "luck", "hit", "speed"]:
            if stat == "maxHealth":
                setattr(player, stat, getattr(player, f"sigillessMaxHealth"))
                continue
            elif stat == "maxMana":
                    setattr(player, stat, getattr(player, f"sigillessMaxMana"))
                    continue
            setattr(player, stat, getattr(player, f"sigilless{stat.capitalize()}"))

        # Reset Player Sigils
        for sigil in player.sigils:
            for stat, amount in sigil.statChange:
                setattr(player, stat, getattr(player, stat) + amount)
        
        if player.health > player.maxHealth:
            player.health = player.maxHealth
        
        if player.mana > player.maxMana:
             player.mana = player.maxMana
          
        current = player.savedMaps.get(player.location)

        if current is None:
            template = Map.allMaps.get(player.location)

            if template:
                current = copy.deepcopy(template)
                player.savedMaps[player.location] = current
            else:
                print(f"Unknown location: {player.location}")
                input("!?>")
                innerLoop = False
                break

        run(current, player)