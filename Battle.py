from Utility import *
from gameData.Data import *

BATTLELOG = None

def actionTime(entity, enemy, player, type_=None, theme=None):
    global playerLowHealth, sanityChecked, enemyLowHealth
    
    choice = ""

    if entity == "player" and (player.health > 0 or any(s.name == "Phoenix Blessing" for s in player.statusList)):
        if theme:
            theme = themeDescription(theme)

        player.actions += 1
        escapeChance = max(1, min(99, round(player.luck * 0.50)))
        if type_ is not None and type_ in ["Boss Map/Main", "Extreme", "Gauntlet", "Seasson Boss", "Raid Normal", "Raid Boss"]:
            escapeChance = 0
        say(f"{player.name} Action!")
        while choice not in {"1", "2", "3", "5"}:
            choice = ""
            clear()
            line("battle")

            print(f"{player.name} Stats:")
            print(f"Health: {Color['red']}{player.health}/{player.maxHealth}{Color['reset']} | Mana: {Color['blue']}{player.mana}/{player.maxMana}{Color['reset']} | Sanity: {(Color['yellow'] if player.sanity > 0 else Color['magenta'] if player.sanity < 0 else Color['reset'])}{player.sanity}{Color['reset']}")
            print(f"Strength: {Color['cyan']}{player.strength}{Color['reset']} | Magic: {Color['cyan']}{player.magic}{Color['reset']}")
            print(f"Defense: {Color['cyan']}{player.defense}{Color['reset']} | Resistance: {Color['cyan']}{player.resistance}{Color['reset']}")
            print(f"Luck: {Color['yellow']}{player.luck}{Color['reset']} | Hit: {Color['yellow']}{player.hit}{Color['reset']} | Speed: {Color['yellow']}{player.speed}{Color['reset']}")
            print(f"Statuses: {Color['green']}{', '.join(Color['green' if s.align == 'Positive' else 'red' if s.align == 'Negative' else 'yellow'] + f'{s.name} ({s.duration}/{s.maxDuration if not s.forever else '∞'})' + (f' [{s.stacks}/{s.maxStack}]' if s.canStack else '') + Color['reset'] for s in player.statusList) or 'None'}{Color['reset']}")
            line("battle")
            
            print(f"{enemy.name} Stats:")
            print(f"Health: {Color['red']}{enemy.health}/{enemy.maxHealth}{Color['reset']} | Sanity: {(Color['yellow'] if enemy.sanity > 0 else Color['magenta'] if enemy.sanity < 0 else Color['reset'])}{enemy.sanity}{Color['reset']}")
            print(f"Strength: {Color['cyan']}{enemy.strength}{Color['reset']} | Magic: {Color['cyan']}{enemy.magic}{Color['reset']}")
            print(f"Defense: {Color['cyan']}{enemy.defense}{Color['reset']} | Resistance: {Color['cyan']}{enemy.resistance}{Color['reset']}")
            print(f"Luck: {Color['yellow']}{enemy.luck}{Color['reset']} | Hit: {Color['yellow']}{enemy.hit}{Color['reset']} | Speed: {Color['yellow']}{enemy.speed}{Color['reset']}")
            print(f"Statuses: {Color['green']}{', '.join(Color['green' if s.align == 'Positive' else 'red' if s.align == 'Negative' else 'yellow'] + f'{s.name} ({s.duration}/{s.maxDuration if not s.forever else '∞'})' + (f' [{s.stacks}/{s.maxStack}]' if s.canStack else '') + Color['reset'] for s in enemy.statusList) or 'None'}{Color['reset']}")
            print(f"F: {symbols.get(enemy.fire)} | I: {symbols.get(enemy.ice)} | T: {symbols.get(enemy.thunder)} | W: {symbols.get(enemy.wind)} | M: {symbols.get(enemy.mighty)} | P: {symbols.get(enemy.physical)}")
            line("battle")
            
            if any(s.name in ["Phoenix Blessing"] for s in player.statusList) and player.health <= 0:
                player.lastAction = "Revive"
                return None   
                        
            if not playerLowHealth and player.health <= round(player.maxHealth * 0.30):
                player.sanity -= 5
                playerLowHealth = True
                say(f"{Color['magenta']}Health Reached 30%! Sanity Was Reduced By 5!{Color['reset']}")
                line("battle")
                input("?>")

            if any("Stun" in s.type_ for s in player.statusList):
                player.lastAction = "Stun"
                say(f"{Color['green']}{player.name} Cannot Act!{Color['reset']}")
                line("battle")
                input("?>")
                return None
            
            if sanityChecked:
                sanityCheck(player, enemy, "player")
                sanityChecked = False

            # Options 
            print(f"1. {Color['red']}Attack{Color['reset']} |",
                f"2. {Color['magenta']}Skill{Color['reset']} |",
                f"3. {Color['cyan']}Item{Color['reset']} |",
                f"4. {Color['yellow']}Analyze{Color['reset']} |",
                f"5. {Color['yellow']}Escape {escapeChance}%{Color['reset']} | "
                f"6. Wait")
            line("battle")

            choice = input("->")
            if choice == "1":
                return player.attack(player, enemy, actions)

            elif choice == "2":
                choice = ""
                clear()
                print(f"{Color['magenta']}Skills{Color['reset']}")
                line("battle")

                for i in range(1, len(player.skills) + 1):            
                    print(f"{i}. {Color['cyan'] if player.skills[i - 1].usable and not 'Passive' in player.skills[i - 1].type_ else Color['blue'] if 'Passive' in player.skills[i - 1].type_ else Color['magenta']}{player.skills[i - 1].name}{' | ' + player.skills[i - 1].sanLean if "Damage" in player.skills[i - 1].type_ else ''}{f' | Element: {(player.skills[i - 1].element.capitalize())}' if player.skills[i - 1].element != None else ""}{f' | Cost: {player.skills[i - 1].cost + round(player.sigillessMaxMana * 0.06)}' if not 'Passive' in player.skills[i - 1].type_ else ""}{f' | Hit: {player.skills[i - 1].hit}' if player.skills[i - 1].hit > 0 else ""}{f' | Critical: {player.skills[i - 1].critical}' if player.skills[i - 1].critical > 0 else ""}{f' | Cooldown: {f'{player.skills[i - 1].cooldownProgress}/{player.skills[i - 1].cooldown}'}' if player.skills[i - 1].cooldown > 0 else ""} | Usable: {player.skills[i - 1].usable if "Passive" not in player.skills[i - 1].type_ else 'False'}{Color['reset']}")
                    text = Color['yellow'] + player.skills[i - 1].text + Color['reset']
                    names = sorted(Status.allStatuses.keys(), key=len, reverse=True)
                    pattern = r"\b(" + "|".join(map(re.escape, names)) + r")\b"
                    text = re.sub(pattern, lambda m: colorize(m, Status), text)
                    print(text)
                    
                    shown = set()
                    for status in Status.allStatuses.values():
                        printStatus(status, player.skills[i - 1], shown)
                    line("basicOther")
                print(f"0.{Color['red']}Back{Color['reset']}")
                line("battle")

                while choice not in {str(i) for i in range(0, len(player.skills) + 1)}:
                    choice = input("->")

                    if choice in {str(i) for i in range(1, len(player.skills) + 1)}:
                        skillIndex = int(choice) - 1
                        if player.skills[skillIndex].usable == False:
                            print("Skill Is On Cooldown!")
                            input("?>")
                            choice = "0"

                        elif player.skills[skillIndex].cost + round(player.sigillessMaxMana * 0.06) > player.mana:
                            print("Not Enough Mana!")
                            input("?>")
                            choice = "0"
                        
                        elif "Passive" in player.skills[skillIndex].type_:
                            print("Can'player use Passive skills!")
                            input("?>")
                            choice = "0"

                        else:
                            player.mana -= player.skills[skillIndex].cost + round(player.sigillessMaxMana * 0.06)
                            return player.skills[skillIndex].effect(player, enemy, actions)
                    
                    if choice == "0":
                        choice = ""
                        break
            
            elif choice == "3":
                choice = ""
                page = []
                currentPage = 0

                while True:
                    clear()
                    print(f"{Color['cyan']}Items{Color['reset']}")
                    line("battle")

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
                        line("battle")
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
                                
                            number += 1
                            if number != len(pages[currentPage]):
                                print("")
                    else:
                        print("No Items!")
                    line("battle")

                    print(f"U + Item Number (Use)\n"
                          "0. Back")
                    if currentPage + 1 < len(pages): print("1. Next Page")
                    if currentPage > 0: print("2. Previous Page")
                    line("battle")

                    itemChoice = input("->")

                    if itemChoice.startswith("u") or itemChoice.startswith("U"):
                        idx = itemChoice[1:]
                        if pages and idx.isdigit() and int(idx) < len(pages[currentPage]):
                            chosen = pages[currentPage][int(idx)]
                            if chosen.useType == "Overworld":
                                print(f"{Color['red']}You Can'player Use This Item In Battle!{Color['reset']}")
                                input("?>")
                                break
                            player.lastItem = chosen
                            player.lastAction = "Item"
                            return chosen.use(player, enemy)

                    elif itemChoice == "0":
                        choice = ""  
                        break

                    elif itemChoice == "1" and currentPage + 1 < len(pages):
                        currentPage += 1

                    elif itemChoice == "2" and currentPage > 0:
                        currentPage -= 1

            elif choice == "4":
                player.analyze(enemy, theme)

            elif choice == "5":
                player.lastAction = "Escape"
                if escapeChance >= random.randint(1, 100):
                    say(f"{Color['green']}Succesful Escape!{Color['reset']}")
                    input(">")
                    clear()
                    return "Escape"
                
                else:
                    say(f"{Color['red']}Failed Escape!{Color['reset']}")
                    input(">")
                    return None
            
            elif choice == "6":
                player.lastAction = "Wait"
                player.sanity += 3
                say(f"{player.name} Waited!")
                return None

    if entity == "enemy" and (enemy.health > 0 or any(s.name == "Phoenix Blessing" for s in enemy.statusList)):
        enemy.actions += 1
        clear()
        say(f"{enemy.name} Action!")
        line("battle")

        print(f"{player.name} Stats:")
        print(f"Health: {Color['red']}{player.health}/{player.maxHealth}{Color['reset']} | Mana: {Color['blue']}{player.mana}/{player.maxMana}{Color['reset']} | Sanity: {(Color['yellow'] if player.sanity > 0 else Color['magenta'] if player.sanity < 0 else Color['reset'])}{player.sanity}{Color['reset']}")
        print(f"Strength: {Color['cyan']}{player.strength}{Color['reset']} | Magic: {Color['cyan']}{player.magic}{Color['reset']}")
        print(f"Defense: {Color['cyan']}{player.defense}{Color['reset']} | Resistance: {Color['cyan']}{player.resistance}{Color['reset']}")
        print(f"Luck: {Color['yellow']}{player.luck}{Color['reset']} | Hit: {Color['yellow']}{player.hit}{Color['reset']} | Speed: {Color['yellow']}{player.speed}{Color['reset']}")
        print(f"Statuses: {Color['green']}{', '.join(Color['green' if s.align == 'Positive' else 'red' if s.align == 'Negative' else 'yellow'] + f'{s.name} ({s.duration}/{s.maxDuration if not s.forever else '∞'})' + (f' [{s.stacks}/{s.maxStack}]' if s.canStack else '') + Color['reset'] for s in player.statusList) or 'None'}{Color['reset']}")
        line("battle")
        
        print(f"{enemy.name} Stats:")
        print(f"Health: {Color['red']}{enemy.health}/{enemy.maxHealth}{Color['reset']} | Sanity: {(Color['yellow'] if enemy.sanity > 0 else Color['magenta'] if enemy.sanity < 0 else Color['reset'])}{enemy.sanity}{Color['reset']}")
        print(f"Strength: {Color['cyan']}{enemy.strength}{Color['reset']} | Magic: {Color['cyan']}{enemy.magic}{Color['reset']}")
        print(f"Defense: {Color['cyan']}{enemy.defense}{Color['reset']} | Resistance: {Color['cyan']}{enemy.resistance}{Color['reset']}")
        print(f"Luck: {Color['yellow']}{enemy.luck}{Color['reset']} | Hit: {Color['yellow']}{enemy.hit}{Color['reset']} | Speed: {Color['yellow']}{enemy.speed}{Color['reset']}")
        print(f"Statuses: {Color['green']}{', '.join(Color['green' if s.align == 'Positive' else 'red' if s.align == 'Negative' else 'yellow'] + f'{s.name} ({s.duration}/{s.maxDuration if not s.forever else '∞'})' + (f' [{s.stacks}/{s.maxStack}]' if s.canStack else '') + Color['reset'] for s in enemy.statusList) or 'None'}{Color['reset']}")
        print(f"F: {symbols.get(enemy.fire)} | I: {symbols.get(enemy.ice)} | T: {symbols.get(enemy.thunder)} | W: {symbols.get(enemy.wind)} | M: {symbols.get(enemy.mighty)} | P: {symbols.get(enemy.physical)}")
        line("battle")
        
        if any(s.name in ["Phoenix Blessing"] for s in enemy.statusList) and enemy.health <= 0:
            enemy.lastAction = "Revive"
            return None  
        
        if not enemyLowHealth and enemy.health <= round(enemy.maxHealth * 0.30):
            enemy.sanity -= 5
            enemyLowHealth = True
            say(f"{Color['magenta']}Health Reached 30%! Sanity Was Reduced By 5!{Color['reset']}")
            line("battle")
            input("?>")

        if type_ in ["Boss Map/Main", "Extreme", "Gauntlet", "Seasson Boss", "Raid Normal", "Raid Boss"] and enemy.health < round(enemy.maxHealth * 0.5):
            negatives = sum((1 for s in enemy.statusList if s.align == "Negative"), 0)
            if negatives >= 4:
                if (enemy.luck + random.randint(1, 50)) * 2 >= round(random.randint(130, 160) * (1.5)):
                    num = negatives // 2
                    count = 0
                    for status in enemy.statusList[:]:
                        if status.align == "Negative":
                            say(f"{Color['magenta']}{enemy.name} Shook Off Their {status.name}!{Color['reset']}")
                            enemy.statusList.remove(status)
                            count += 1

                        if count >= num:
                            break
                    Fix.statMutation(enemy)
                    line("battle")
      
        if any("Stun" in s.type_ for s in enemy.statusList):
            say(f"{Color['green']}{enemy.name} Cannot Act!{Color['reset']}")
            line("battle")
            input("?>")
            return None
        
        sanityCheck(player, enemy, "enemy")
                    
        if enemy.ultimateMeter >= 70:
            enemy.lastAction = "Ultimate"
            enemy.ultimateMeter -= 70
            if isinstance(enemy.ultimateSkill, list):
                return random.choice(enemy.ultimateSkill).effect(enemy, player)
            else:
                return enemy.ultimateSkill.effect(enemy, player)
        return enemy.behavior(enemy, player, actions)
    
def infoDisplay(enemy, player):
    # Player Tracking
    total = min(20, player.maxHealth // 10)
    filled = round((player.health / player.maxHealth) * total)
    filled = max(0, min(total, filled))
    meter = f"{Color['red']}▮{Color['reset']}" * filled + "▯" * (total - filled)
    print(f"{player.name} Health: {meter}") # Health Meter

    meter = ""
    total = min(20, player.maxMana // 10)
    filled = min(total, player.mana // 10)
    filled = max(0, filled)
    meter = f"{Color['blue']}▮{Color['reset']}" * filled + "▯" * (total - filled)
    print(f"{player.name} Mana: {meter}") # Mana Meter

    print(f"Health: {Color['red']}{player.health}/{player.maxHealth}{Color['reset']} | Mana: {Color['blue']}{player.mana}/{player.maxMana}{Color['reset']}")
    print(f"Strength: {Color['cyan']}{player.strength}{Color['reset']} | Magic: {Color['cyan']}{player.magic}{Color['reset']}")
    print(f"Defense: {Color['cyan']}{player.defense}{Color['reset']} | Resistance: {Color['cyan']}{player.resistance}{Color['reset']}")
    print(f"Luck: {Color['yellow']}{player.luck}{Color['reset']} | Hit: {Color['yellow']}{player.hit}{Color['reset']} | Speed: {Color['yellow']}{player.speed}{Color['reset']}")
    print(f"Statuses: {Color['green']}{', '.join(Color['green' if s.align == 'Positive' else 'red' if s.align == 'Negative' else 'yellow'] + f'{s.name} ({s.duration}/{s.maxDuration if not s.forever else '∞'})' + (f' [{s.stacks}/{s.maxStack}]' if s.canStack else '') + Color['reset'] for s in player.statusList) or 'None'}{Color['reset']}")
    line("basic")

    meter = ""
    for i in range(0, 100, 10):
        if player.speedMeter > i:
            meter += f"{Color['yellow']}▮{Color['reset']}>"
        else:
            meter += f"{Color['yellow']}▯{Color['reset']}>"
    meter = "-" + meter
    print("Speed Meter: " + meter) # Speed Tracker

    if player.buddy:
        meter = ""
        for i in range(0, 150, 15):
            if player.buddy.buddyMeter > i:
                meter += f"{Color['cyan']}▮{Color['reset']}>"
            else:
                meter += f"{Color['cyan']}▯{Color['reset']}>"
        meter = "-" + meter
        print("Buddy Meter: " + meter) # Buddy Tracker
    
    meter = ""
    for i in range(-5, 6):
        if i < 0:
            if player.sanity <= i * 5:
                meter += f"{Color['magenta']}▮{Color['reset']}"
            else:
                meter += "▯"
        elif i == 0:
            meter += "|"
        elif i > 0:
            if player.sanity >= i * 5:
                meter += f"{Color['yellow']}▮{Color['reset']}"
            else:
                meter += "▯"
    print("Sanity Meter: " + meter) # Sanity Tracker
    line("basicOther")

    # Enemy Tracking
    meter = ""
    total = min(20, enemy.maxHealth // 10)
    filled = round((enemy.health / enemy.maxHealth) * total)
    filled = max(0, min(total, filled))
    meter = f"{Color['red']}▮{Color['reset']}" * filled + "▯" * (total - filled)
    print(f"{enemy.name} Health: {meter}")

    print(f"Health: {Color['red']}{enemy.health}/{enemy.maxHealth}{Color['reset']}")
    print(f"Strength: {Color['cyan']}{enemy.strength}{Color['reset']} | Magic: {Color['cyan']}{enemy.magic}{Color['reset']}")
    print(f"Defense: {Color['cyan']}{enemy.defense}{Color['reset']} | Resistance: {Color['cyan']}{enemy.resistance}{Color['reset']}")
    print(f"Luck: {Color['yellow']}{enemy.luck}{Color['reset']} | Hit: {Color['yellow']}{enemy.hit}{Color['reset']} | Speed: {Color['yellow']}{enemy.speed}{Color['reset']}")
    print(f"Statuses: {Color['green']}{', '.join(Color['green' if s.align == 'Positive' else 'red' if s.align == 'Negative' else 'yellow'] + f'{s.name} ({s.duration}/{s.maxDuration if not s.forever else '∞'})' + (f' [{s.stacks}/{s.maxStack}]' if s.canStack else '') + Color['reset'] for s in enemy.statusList) or 'None'}{Color['reset']}")
    print(f"F: {symbols.get(enemy.fire)} | I: {symbols.get(enemy.ice)} | T: {symbols.get(enemy.thunder)} | W: {symbols.get(enemy.wind)}| M: {symbols.get(enemy.mighty)} | P: {symbols.get(enemy.physical)}")
    line("basic")

    meter = ""
    for i in range(0, 100, 10):
        if enemy.speedMeter > i:
            meter += f"{Color['yellow']}▮{Color['reset']}>"
        else:
            meter += f"{Color['yellow']}▯{Color['reset']}>"
    meter = "-" + meter
    print("Speed Meter: " + meter) # Speed Tracker

    meter = ""
    for i in range(-5, 6):
        if i < 0:
            if enemy.sanity <= i * 5:
                meter += f"{Color['magenta']}▮{Color['reset']}"
            else:
                meter += "▯"
        elif i == 0:
            meter += "|"
        elif i > 0:
            if enemy.sanity >= i * 5:
                meter += f"{Color['yellow']}▮{Color['reset']}"
            else:
                meter += "▯"
    print("Sanity Meter: " + meter) # Sanity Tracker
    line("basicOther")

    meter = ""
    for i in range(0, 70, 10):
        if enemy.ultimateMeter > i:
            meter += f"{Color['magenta']}▮{Color['reset']}!"
        else:
            meter += f"{Color['magenta']}▯{Color['reset']}!"
    meter = "-" + meter
    print("Ultimate Meter: " + meter) # Ultimate Tracker
    line("basicOther")

def meterTrack(enemy, player, type_):
    spd = player.speed
    # Player Lucky Speed Boost
    if player.luck + random.randint(25, 50) >= random.randint(1, 700):
        spd += random.randint(10, 15)

    for status in player.statusList:
        spd = status.speedInterupt(player, spd)

    player.speedMeter += spd
    
    # Player Buddy
    if player.buddy:
        player.buddy.buddyMeter += round(player.speed * 0.25) + player.buddy.speed

    spd = enemy.speed
    # Enemy Lucky Speed Boost
    if enemy.luck + random.randint(25, 50) >= random.randint(1, 700):
        spd += random.randint(10, 15)

    for status in enemy.statusList:
        spd = status.speedInterupt(enemy, spd)

    enemy.speedMeter +=  spd
    
    # Enemy Speed Debuff Ticks
    if not hasattr(enemy, "ticks"):
        enemy.ticks = 0
    
    if type_ in ["Boss Map/Main", "Extreme", "Gauntlet", "Seasson Boss", "Raid Normal", "Raid Boss"]:
        if any("Debuff" in s.type_ and any(i[0] == "speed" and i[1]<0 for i in s.mutate) for s in enemy.statusList):
            if player.speedMeter - 50 > enemy.speedMeter and enemy.luck * 0.5 + random.randint(1, 100) > 105 or enemy.health <= round(enemy.maxHealth * 0.40) and enemy.luck * 0.65 + random.randint(1, 75) > 125:
                for status in enemy.statusList[:]:
                    if "Debuff" in status.type_ and any(s[0] == "speed" and s[1] < 0 for s in status.mutate):
                        say(f"{Color['magenta']}{enemy.name} Shook Off Their {status.name}! {enemy.name}s Speed Meter Was Raised By 6!{Color['reset']}")
                        enemy.statusList.remove(status)
                        enemy.speedMeter += 6

                Fix.statMutation(enemy)
                line("battle")
                input(">")
                      
    # Ultimate Meter
    if actions % 5 == 0 and actions != 0:
        enemy.ultimateMeter += enemy.speed // 5
    
    else:
        enemy.ultimateMeter += 3

def skillCooldownTrack(player):
    for skill in player.skills:
        skill.turnCooldown()
        if skill.cooldown < 0:
            skill.cooldown = 0

def sigilEffects(player, enemy, trigger, tickStatus=None, result=0):
    re = False
    for sigil in player.sigils:
        if sigil.battleEffect and sigil.trigger == trigger:
            sigil.battleEffect(sigil, player, enemy, tickStatus, result, actions)
            re = True

    if re:
        return True

def passiveEffects(player, enemy, who, damage=0):
    if who == "player":
        for skill in player.skills:
            if "Passive" in skill.type_ and skill.usable:
                skill.passive(player, enemy, damage)
    
    if who == "enemy":
        for skill in enemy.skills:
            if "Passive" in skill.type_ and skill.usable:
                skill.passive(enemy, player, damage)

def buddyEffects(player, enemy, result, actions):
    player.buddy.passive.passive(player, enemy, result)
    
    if player.buddy.buddyMeter >= 150:
        player.buddy.skill.effect(player.buddy, player, enemy, result, actions)
        player.buddy.buddyMeter -= 150

def statusDurationTracker(target, enemy, player, damage=0):
    if target == "player":
        for status in player.statusList[:]:
            sigilEffects(player, enemy, "statusTick", tickStatus=status)
            if status in player.statusList:
                if status.canStack and status.stacks <= 0:
                    status.remove(player, full=True)
                    continue
                if any(player in ("Damage", "Debuff", "Buff", "Prolonger", "Heal", "Sanity", "Shift") for player in status.type_) and "Special" not in status.type_:
                    status.simple(player)
                elif "Counter" in status.type_ and isinstance(damage, int):
                    status.simple(player, damage, enemy)
                elif "Special" in status.type_:
                    status.special(player, damage if isinstance(damage, int) else 0, enemy)
                if status in player.statusList:
                    status.turnIncrement(player)

    if target == "enemy":
        for status in enemy.statusList[:]:
            sigilEffects(player, enemy, "statusTickEnemy", tickStatus=status)
            if status in enemy.statusList:
                if status.canStack and status.stacks <= 0:
                    status.remove(enemy, full=True)
                    continue
                if any(player in ("Damage", "Debuff", "Buff", "Prolonger", "Heal", "Sanity", "Shift") for player in status.type_) and "Special" not in status.type_:
                    status.simple(enemy)
                elif "Counter" in status.type_ and isinstance(damage, int):
                    status.simple(enemy, damage, player)
                elif "Special" in status.type_:
                    status.special(enemy, damage if isinstance(damage, int) else 0, player)
                if status in enemy.statusList:
                    status.turnIncrement(enemy)
    
    if player.health < 0:
        player.health = 0
    if player.mana < 0:
        player.mana = 0
    
    if enemy.health < 0:
        enemy.health = 0

def statusExist(player, enemy):
    for status in player.statusList:
        status.coexistCheck(player)
        if status.canStack and status.stacks <= 0:
            status.remove(player, full=True)
    
    for status in enemy.statusList:
        status.coexistCheck(enemy)
        if status.canStack and status.stacks <= 0:
            status.remove(enemy, full=True)

def statusRewards(player, coinReward, gpReward):
    for status in player.statusList:
        if status.name == "Golden":
            coinReward += round(coinReward * (status.stacks / 100))
            gpReward += round(gpReward * (status.stacks / 100))
    
        if status.name == "Diamond":
            coinReward += round(coinReward * 0.35)
            gpReward += round(gpReward * 0.35)

        if status.name == "Stolen Goods":
            coinReward += round(coinReward * (0.05 * status.stacks))
            gpReward += round(gpReward * (0.05 * status.stacks))

            chance = 0.1 + (player.luck // 10) * 0.02
            pool = [i for i in Item.allItems.values() if "Damage" in i.type_]

            for i in range(0, min(3, status.stacks)):
                if chance >= random.random():
                    print(f"{Color['yellow']}Stolen Goods Triggered!{Color['reset']}")
                    amount = random.randint(1,3)
                    item = random.choice(pool)
                    item.tracker(amount, "Add", player)
                    print(f"{Color['yellow']}{player.name} Gained {amount} {item.name}!{Color['reset']}")

    return coinReward, gpReward

def sanityCheck(player, enemy, target):
    if target == "player":
        # Positive Sanity
        if player.sanity >= 5 and player.sanity < 10 and not any("Boost I" == s.name for s in player.statusList):
            Status.allStatuses["Boost I"].inflict(player)

        elif player.sanity >= 10 and player.sanity < 15 and not any("Tough I" == s.name for s in player.statusList):
            Status.allStatuses["Tough I"].inflict(player)

        elif player.sanity >= 15 and player.sanity < 20 and not any("Boost II" == s.name for s in player.statusList):
            Status.allStatuses["Boost II"].inflict(player)

        elif player.sanity >= 20 and player.sanity < 25 and not any("Tough II" == s.name for s in player.statusList):
            Status.allStatuses["Tough II"].inflict(player)

        elif player.sanity >= 25 and not any("Tranquil" == s.name for s in player.statusList):
            Status.allStatuses["Tranquil"].inflict(player)
        
        if player.sanity >= sanityCaps[0]:
            player.sanity -= sanityCaps[0]
        
        # Passives (Positive)
        if player.sanity >= 5:
            heal = player.sanity // 2
            player.mana += heal
            player.mana = min(player.maxMana, player.mana)
            say(f"{Color['blue']}{player.name}s Mana Was Restored By {heal}!{Color['reset']}")
        
        if player.sanity >= 10:
            amount = 0
            for status in player.statusList:
                if amount >= 2:
                    break
                if random.randint(1,100) >= 50 and status.align == "Positive":
                    status.duration -= 1
                    say(f"{Color['yellow']}{status.name} Had Its Duration Extended By 1!{Color['reset']}")
                    amount += 1
                if status.duration < 0:
                    status.duration = 0

        # Negative Sanity
        if player.sanity <= -5 and player.sanity > -10 and not any("Clouded I" == s.name for s in player.statusList):
            Status.allStatuses["Clouded I"].inflict(player)

        elif player.sanity <= -10 and player.sanity > -15 and not any("Consumed" == s.name for s in player.statusList):
            Status.allStatuses["Consumed"].inflict(player)

        elif player.sanity <= -15 and player.sanity > -20 and not any("Clouded II" == s.name for s in player.statusList):
            Status.allStatuses["Clouded II"].inflict(player)

        elif player.sanity <= -20 and player.sanity > -25 and not any("Sinking" == s.name for s in player.statusList):
            Status.allStatuses["Sinking"].inflict(player)

        elif player.sanity <= -25:
            Status.allStatuses["Sinking"].inflict(player, 2)
        
        if player.sanity <= sanityCaps[1]:
            player.sanity -= sanityCaps[1]
        
        # Passives (Negatives)
        if player.sanity <= -5:
            player.speedMeter -= random.randrange(5, 15, 5)
            player.speedMeter = max(-25, player.speedMeter)
            say(f"{Color['magenta']}{player.name} Will Now Act Slower!{Color['reset']}")
        
        if player.sanity <= -10:
            amount = 0
            for status in player.statusList:
                if amount >= 2:
                    break
                if random.randint(1,100) >= 50 and status.align == "Negative":
                    status.duration -= 1
                    say(f"{Color['magenta']}{status.name} Had Its Duration Extended By 1!{Color['reset']}")
                    amount += 1
                if status.duration < 0:
                    status.duration = 0

    elif target == "enemy":
        # Positive Sanity
        if enemy.sanity >= 5 and enemy.sanity < 10 and not any("Boost I" == s.name for s in enemy.statusList):
            Status.allStatuses["Boost I"].inflict(enemy)

        elif enemy.sanity >= 10 and enemy.sanity < 15 and not any("Tough I" == s.name for s in enemy.statusList):
            Status.allStatuses["Tough I"].inflict(enemy)

        elif enemy.sanity >= 15 and enemy.sanity < 20 and not any("Boost II" == s.name for s in enemy.statusList):
            Status.allStatuses["Boost II"].inflict(enemy)

        elif enemy.sanity >= 20 and enemy.sanity < 25 and not any("Tough II" == s.name for s in enemy.statusList):
            Status.allStatuses["Tough II"].inflict(enemy)

        elif enemy.sanity >= 25:
            Status.allStatuses["Boost III"].inflict(enemy)
        
        if enemy.sanity >= sanityCaps[0]:
            enemy.sanity -= sanityCaps[0]
        
        # Passives (Positive)
        if enemy.sanity >= 5:
            heal = enemy.sanity // 2
            enemy.health += heal
            enemy.health = min(enemy.maxHealth, enemy.health)
            say(f"{Color['blue']}{enemy.name}s Health Was Restored By {heal}!{Color['reset']}")
        
        if enemy.sanity >= 10:
            amount = 0
            for status in enemy.statusList:
                if amount >= 2:
                    break
                if random.randint(1,100) >= 50 and status.align == "Positive":
                    status.duration -= 1
                    say(f"{Color['yellow']}{status.name} Had Its Duration Extended By 1!{Color['reset']}")
                    amount += 1
                if status.duration < 0:
                    status.duration = 0
        # Negative Sanity
        if enemy.sanity <= -5 and enemy.sanity > -10 and not any("Clouded I" == s.name for s in enemy.statusList):
            Status.allStatuses["Clouded I"].inflict(enemy)

        elif enemy.sanity <= -10 and enemy.sanity > -15 and not any("Consumed" == s.name for s in enemy.statusList):
            Status.allStatuses["Consumed"].inflict(enemy)

        elif enemy.sanity <= -15 and enemy.sanity > -20 and not any("Clouded II" == s.name for s in enemy.statusList):
            Status.allStatuses["Clouded II"].inflict(enemy)

        elif enemy.sanity <= -20 and enemy.sanity > -25 and not any("Sinking" == s.name for s in enemy.statusList):
            Status.allStatuses["Sinking"].inflict(enemy)

        elif enemy.sanity <= -25:
            Status.allStatuses["Frail III"].inflict(enemy)
        
        if enemy.sanity <= sanityCaps[1]:
            enemy.sanity -= sanityCaps[1]

        # Passives (Negatives)
        if enemy.sanity <= -5:
            enemy.speedMeter -= random.randrange(5, 15, 5)
            enemy.speedMeter = max(-25, enemy.speedMeter)
            say(f"{Color['magenta']}{enemy.name} Will Now Act Slower!{Color['reset']}")
        
        if enemy.sanity <= -10:
            amount = 0
            for status in enemy.statusList:
                if amount >= 2:
                    break
                if random.randint(1,100) >= 50 and status.align == "Negative":
                    status.duration -= 1
                    say(f"{Color['magenta']}{status.name} Had Its Duration Extended By 1!{Color['reset']}")
                    amount += 1
                if status.duration < 0:
                    status.duration = 0

def resetBattleState(self, type_=None):
    if type_ != "Survival":
        self.statusList.clear()
    
    if isinstance(self, Player):
        for stat in ["maxHealth", "maxMana", "strength", "magic", "defense", "resistance", "luck", "hit", "speed"]:
            if stat == "maxHealth":
                setattr(self, stat, getattr(self, f"sigillessMaxHealth"))
                continue
            elif stat == "maxMana":
                    setattr(self, stat, getattr(self, f"sigillessMaxMana"))
                    continue
            setattr(self, stat, getattr(self, f"sigilless{stat.capitalize()}"))

        for sigil in self.sigils:
            for stat, amount in sigil.statChange:
                setattr(self, stat, getattr(self, stat) + amount)
                
    if isinstance(self, Enemy):
        for stat in ["strength", "magic", "defense", "resistance", "luck", "hit", "speed"]:
            setattr(self, stat, getattr(self, f"base{stat.capitalize()}"))

    self.lastSkill = None
    self.lastAction = None

def themeEffects(theme, target, opposer, actions, who):
    global sanityCaps
    
    if isinstance(theme, list):
        if theme[0] == "summer":
            Burn.inflict(target)
            if any("Burn" == s.name and s.stacks == s.maxStack for s in target.statusList):
                Heated.inflict(target)
            
            if (target.lastAction and target.lastAction == "Skill" and target.lastSkill and "Damage" in target.lastSkill.type_ and target.lastSkill.element == "fire"):
                if random.randint(1, 100) >= 40:
                    Sear.inflict(opposer)
                else:
                    Sear.inflict(target)

        elif theme[0] == "winter":
            if random.randint(1,100) >= 90:
                DeepFreeze.inflict(target)
            
            if any("Chill" == s.family for s in target.statusList):
                if random.randint(1,100) >= 90:
                    FrailI.inflict(target)
                    CrippleI.inflict(target)
            
            if (target.lastAction and target.lastAction == "Skill" and target.lastSkill and "Damage" in target.lastSkill.type_ and target.lastSkill.element == "ice"):
                Freeze.inflict(opposer)

        elif theme[0] == "fall":
            status = [Shock, Overload, Static]
            random.choice(status).inflict(target)

            count = sum(1 for s in target.statusList if s.family == "Shock")

            if count == 1:
                BoostI.inflict(target)

            if count == 2:
                BoostII.inflict(target)

            if count >= 3:
                BoostIII.inflict(target)

            if (target.lastAction and target.lastAction == "Skill" and target.lastSkill and "Damage" in target.lastSkill.type_ and target.lastSkill.element == "thunder"):
                Static.inflict(opposer)

        elif theme[0] == "spring":
            status = [stat for stat in Status.allStatuses.values() if stat.family in ["Poison", "Bleed"]]
            random.choice(status).inflict(target)

            for status in target.statusList:
                if status.family == "Poison":
                    status.count += 2
                    say(f"{Color['magenta']}{status.name}s Count Was Increased By 2 Due To {status.name}!{Color['reset']}")
                
                if status.family in ["Poison", "Bleed"]:
                    if "Special" in status.type_:
                        status.special(target, 0, opposer)
                    else:
                        status.simple(target)

            if (target.lastAction and target.lastAction == "Skill" and target.lastSkill and "Damage" in target.lastSkill.type_ and target.lastSkill.element == "wind"):
                if random.randint(1, 100) >= 40:
                    status = [stat for stat in Status.allStatuses.values() if stat.family == "Bleed" and stat.align == "Negative"]
                    random.choice(status).inflict(opposer)

    else:
        if theme == "leech":
            enemy = target if isinstance(target, Enemy) else opposer
            player = target if not isinstance(target, Enemy) else opposer

            if target == player and player.lastAction and player.lastAction == "Skill":
                cost = player.lastSkill.cost // 2
                player.mana -= cost
                say(f"{Color['red']}{player.name} Lost {cost} Mana!{Color['reset']}")

                if random.randint(1, 100) >= 70:
                    Husk.inflict(player)

        elif theme == "dread":
            if isinstance(target, Player):
                say(f"{Color['magenta']}{target.name} Lost 2 Sanity!{Color['reset']}")
                target.sanity -= 2

            if target.sanity <= -12:
                Gloom.inflict(target)

        elif theme == "thdk":
            enemy = target if isinstance(target, Enemy) else opposer
            player = target if not isinstance(target, Enemy) else opposer
            
            if enemy.actions <= 1 and not any(s.name in ["Sapien Head", "Temerarios Head", "Fomes Head"] for s in enemy.statusList):
                enemy.statusList.append(copy.deepcopy(Sapien))
                enemy.statusList.append(copy.deepcopy(Temerarios))
                enemy.statusList.append(copy.deepcopy(Fomes))
            
            for status in enemy.statusList[:]:
                if status.name == "Sapien Head":
                    if player.lastAction and player.lastAction == "Skill" and player.lastSkill and "Damage" in player.lastSkill.type_ and "ice" == player.lastSkill.element:
                        if enemy == opposer:
                            status.count -= 3
                            say(f"{Color['red']}{player.name}s {status.name} Lost 3 Count!{Color['reset']}")

                        if status.count <= 0:
                            enemy.skills.remove(next(s for s in enemy.skills if s.name == "Waking Avalanche"))
                            enemy.skills.remove(next(s for s in enemy.skills if s.name == "Icy Barrier"))
                            enemy.ultimateSkill.remove(next(s for s in enemy.ultimateSkill if s.name == "Diamond Dust"))
                            enemy.statusList.remove(status)
                            continue

                    if not any(s.name in ["Waking Avalanche", "Icy Barrier"] for s in enemy.skills):
                        enemy.skills.append(copy.deepcopy(bskill_waking_avalanche))
                        enemy.skills.append(copy.deepcopy(bskill_icy_barrier))
                        enemy.ultimateSkill.append(copy.deepcopy(ubskill_diamond_dust))
                        
                elif status.name == "Temerarios Head":
                    if player.lastAction and player.lastAction == "Skill" and player.lastSkill and "Damage" in player.lastSkill.type_ and "fire" == player.lastSkill.element:
                        if enemy == opposer:
                            status.count -= 3
                            say(f"{Color['red']}{player.name}s {status.name} Lost 3 Count!{Color['reset']}")

                        if status.count <= 0:
                            enemy.skills.remove(next(s for s in enemy.skills if s.name == "Mega Flare Impact"))
                            enemy.skills.remove(next(s for s in enemy.skills if s.name == "Blazing Heart"))
                            enemy.ultimateSkill.remove(next(s for s in enemy.ultimateSkill if s.name == "Giga Flare Impact"))
                            enemy.statusList.remove(status)
                            continue

                    if not any(s.name in ["Mega Flare Impact", "Blazing Heart"] for s in enemy.skills):
                        enemy.skills.append(copy.deepcopy(bskill_flare_impact))
                        enemy.skills.append(copy.deepcopy(bskill_blazing_heart))
                        enemy.ultimateSkill.append(copy.deepcopy(ubskill_giga_impact))
                                        
                elif status.name == "Fomes Head":
                    if player.lastAction and player.lastAction == "Skill" and player.lastSkill and "Damage" in player.lastSkill.type_ and "mighty" == player.lastSkill.element:
                        if enemy == opposer:
                            status.count -= 3
                            say(f"{Color['red']}{player.name}s {status.name} Lost 3 Count!{Color['reset']}")

                        if status.count <= 0:
                            enemy.skills.remove(next(s for s in enemy.skills if s.name == "Primaeval Rupture"))
                            enemy.skills.remove(next(s for s in enemy.skills if s.name == "Planning King"))
                            enemy.ultimateSkill.remove(next(s for s in enemy.ultimateSkill if s.name == "Imposing Aura"))
                            enemy.statusList.remove(status)
                            continue

                    if not any(s.name in ["Primaeval Rupture", "Planning King"] for s in enemy.skills):
                        enemy.skills.append(copy.deepcopy(bskill_primaeval_rupture))
                        enemy.skills.append(copy.deepcopy(bpassive_planning_king))
                        enemy.ultimateSkill.append(copy.deepcopy(ubskill_imposing_aura))

            heads = any(s.name in ["Sapien Head", "Temerarios Head", "Fomes Head"] for s in enemy.statusList)
            kit = any(s.name in ["Feast", "Prime Dragon King"] for s in enemy.skills)

            if not heads and not kit:
                say(f"{Color['red']}{enemy.name} Lost It's 3 Heads! It Can Now Be Damaged!{Color['reset']}")
                enemy.skills.append(copy.deepcopy(bskill_feast))
                enemy.skills.append(copy.deepcopy(bpassive_dragon_king))
                enemy.ultimateSkill.append(copy.deepcopy(ubskill_king_of_monsters))
            
            elif heads and kit:
                enemy.skills.remove(next(s for s in enemy.skills if s.name == "Feast"))
                enemy.skills.remove(next(s for s in enemy.skills if s.name == "Prime Dragon King"))
                enemy.ultimateSkill.remove(next(s for s in enemy.ultimateSkill if s.name == "King of the Monsters"))

            elif heads and not kit:
                enemy.health = enemy.maxHealth

        elif theme == "hoarah":
            if not any(s.name == "Stagger" for s in target.statusList): Stagger.inflict(target)
            if not any(s.name == "Stagger" for s in opposer.statusList): Stagger.inflict(opposer)
            
            if target.lastAction and target.lastAction == "Wait" and who == "player":
                say(f"{Color['yellow']}{target.name} Lost 20 Stacks Of Stagger!{Color['reset']}")
                next(s for s in target.statusList if s.name == "Stagger").stacks -= 20
                if next(s for s in target.statusList if s.name == "Stagger").stacks < 0:
                    next(s for s in target.statusList if s.name == "Stagger").stacks = 0

        elif theme == "sea":
            enemy = target if isinstance(target, Enemy) else opposer
            player = target if not isinstance(target, Enemy) else opposer

            if not hasattr(enemy, "mode"):
                enemy.mode = "shield"

            if who == "enemy" and enemy.actions == 1:
                say(f"{Color['yellow']}{enemy.name} Is In Shield Mode!{Color['reset']}")

            if who == "enemy" and  enemy.actions % 3 == 0:
                enemy.mode = "shield" if enemy.mode != "shield" else "sword"
                say(f"{Color['yellow']}{enemy.name} Is In {enemy.mode.capitalize()} Mode!{Color['reset']}")

            if who == "enemy" and enemy.mode == "shield" and not any("Stun" in s.type_ for s in enemy.statusList):
                Protection.inflict(enemy)
                ToughII.inflict(enemy)

            elif who == "enemy" and enemy.mode == "sword" and not any("Stun" in s.type_ for s in enemy.statusList):
                if enemy.lastAction == "Skill" and enemy.lastSkill.name == "Scorching Strike":
                    Down.inflict(enemy, 2)

        elif theme == "hazey":
            enemy = target if isinstance(target, Enemy) else opposer
            player = target if not isinstance(target, Enemy) else opposer

            if player.lastAction and player.lastAction == "Wait" and isinstance(player, Player) and who == "player":
                FlameShields.inflict(player, 2)
            
                if actions >= 15:
                    FlameShields.inflict(player)

            if actions >= 15 and not any(s.name == "Flame Shields" and s.stacks >= 10 for s in player.statusList) and isinstance(player, Player) and who == "player":
                damage = round(player.maxHealth * 0.1)
                player.health -= damage
                say(f"{Color['red']}{player.name} Took {damage}!{Color['reset']}")
       
def themeDescription(theme):
    if theme == "leech":
        theme = f"Leech: {Color['blue']}Every time the player uses a skill, lose mana (50% of skills cost) and chance to inflict Husk on the player.{Color['reset']}"
        return theme

    elif theme == "dread":
        theme = f"Dread: {Color['magenta']}Every time the player acts, player loses 2 sanity. If players sanity is below -12, player gains Gloom.{Color['reset']}"
        return theme
    
    elif theme == "thdk":
        theme = f"Three-Headed: {Color['green']}While all Dragon Heads (Sapien, Temerarios, Fomes) are present on the boss, their health will never go below or meet 0. \nWhen one Head dies, two skills and an ultimate will be removed with it. \nIf all Heads are gone, gain 2 skills and 1 ultimate. \nUsing a Ice/Fire/Mighty element skill will damage the Sapien/Teremarios/Fomes Heads."
        return theme
        
    elif theme == "hoarah":
        theme = f"Badlands: {Color['green']}Hoarah: Both battlers will be given the Stagger status/gain Stagger if not present. If either battler uses Wait, their Stagger will lose 20 stacks.{Color['reset']}"
        return theme

    elif theme == "sea":
        theme = f"Wax Stance: {Color['yellow']}The enemy will start the battle in Shield mode. Every 3 enemy actions, shift between Shield/Sword mode. While in Shield mode, the skill Scorching Strike is unusable by the enemy and, if no Stun statuses are present on the enemy, enemy gains 1 stack of Protection/Tough II after acting. While in Sword mode, Scorching Strike will be usable and enemy gains 2 stacks of Down after using Scorching Strike.{Color['reset']}"
        return theme
    
    elif theme == "hazey":
        theme = f"Hazey: {Color['magenta']}Hazey Rain (Theme): If the player waits, player gains 2 stacks of Flame Shields. Starting at 15 global actions, waiting grants 1 extra Flame Shields and if Flame Shields is not present on the player or Flame Shields is not at 10+ stacks, player takes damage (10% of Max Health) after acting.{Color['reset']}"
        return theme
    
SPEED = False
SHIFT = False
RETRY = False
def battleLoop(enemy, player, battleType, timed=False, limit=False, theme=None, specialBattle=False, wave=None):
    global actions, playerLowHealth, enemyLowHealth, sanityChecked, SPEED, SHIFT, RETRY, sanityCaps
    
    outer = True
    oldHealth = player.health
    oldMana = player.mana
    oldItems = copy.deepcopy(player.items)
    enemyCopy = copy.deepcopy(enemy)
    sanityCaps = [25, -25]

    if hasattr(player, "progress"):
        if player.progress != 4:
            battleType = "Raid Normal"
        else:
            battleType = "Raid Boss"

    while outer:
        if player.logs:
            startBattleLog(player, enemy)
            
            battleLog(f"Battle Type: {battleType}")
            
            battleLog("Skills:")
            for s in player.skills:
                battleLog(s.name)
            battleLog("--##--\n")
            
            battleLog("Sigils:")
            for s in player.sigils:
                battleLog(s.name)
            battleLog("--##--\n")
                
            battleLog("Stats:")
            for s in ["maxHealth", "maxMana", "strength", "defense", "magic", "resistance", "luck", "hit", "speed", "level"]:
                battleLog(f"{s.capitalize()}: {getattr(player, s)}")
            battleLog("--##--\n")

        # Battle Start Check
        
        if RETRY:
            player.health = oldHealth
            player.mana = oldMana
            player.items = copy.deepcopy(oldItems)
            enemy = copy.deepcopy(enemyCopy)
            resetBattleState(player, "Survival" if battleType == "Survival" else None)
            RETRY = False
            
        for i in range(len(player.skills)):
            player.skills[i].cooldownProgress = 0
            player.skills[i].usable = True
            player.skills[i].onCooldown = False
        player.speedMeter = 0
        player.battleTriggers = []
        player.lastSkill = None
        player.attackHits = 0
        player.lastItem = None
        player.lastAction = None
        player.wasHit = False
        if battleType != "Survival" or battleType == "Survival" and wave[1] == 1:
            player.sanity = 0
            player.statusList = []
        player.actions = 0
        playerLowHealth = False
        playerDamage = 0
        if player.buddy:
            player.buddy.buddyMeter = 0
            
        enemy.speedMeter = 0
        enemy.ultimateMeter = 0
        enemy.statusList = []
        enemy.lastSkill = None
        enemy.attackHits = 0
        enemy.lastAction = None
        enemy.wasHit = False
        enemy.sanity = 0
        enemy.actions = 0
        enemyLowHealth = False
        enemyDamage = 0
        enemy.tick = 0
        theme = enemy.theme

        actions = 0
        lastActor = ""
        battle = True
        result = sigilEffects(player, enemy, "battleStart")
        if result: input("?>")

        while battle:
            sanityChecked = True
            player.health = max(0, min(player.health, player.maxHealth))
            player.mana = max(0, min(player.mana, player.maxMana))
            enemy.health = max(0, min(enemy.health, enemy.maxHealth))

            clear()
            print(f"Actions: {actions}")
            if timed:
                say(f"Actions Limit: {Color['red']}{limit}{Color['reset']}")
            infoDisplay(enemy, player)
            meterTrack(enemy, player, battleType)

            # Status Coexisting Check
            statusExist(player, enemy)

            # Battler Action
            if player.speedMeter >= 100 and (player.health > 0 or any(s.name == "Phoenix Blessing" for s in player.statusList)):
                actions += 1
                result = actionTime("player", enemy, player, battleType, theme)
                line("battle")

                if result == "Escape":
                    line("basic")
                    say("Player Escaped!")
                    line("basic")
                                    
                    resetBattleState(player)
                    resetBattleState(enemy)
                    enemy.ultimateMeter = 0
    
                    outer = False
                    return "Escape"
                
                if result:
                    if player.lastAction and player.lastAction == "Skill" and player.lastSkill and "Damage" in player.lastSkill.type_:
                        if lastActor == "player":
                            playerDamage += result
                        else:
                            playerDamage = result
                if theme:
                    print("Theme Effect:")
                    themeEffects(theme, player, enemy, actions, "player")
                    line("battle")

                if sum(1 for s in player.skills if "Passive" in s.type_) > 0:
                    print("Passive Effects:")
                    passiveEffects(player, enemy, "player", result)
                    line("battle")

                if player.buddy:
                    print("Buddy Effects:")
                    buddyEffects(player, enemy, result, actions)
                    line("battle")
                    
                if len(player.sigils) > 0:
                    print("Sigil Effects:")
                    sigilEffects(player, enemy, "afterAction", result=result)
                    line("battle")

                if len(player.statusList) > 0:
                    print("Status Effects:")
                    statusDurationTracker("player", enemy, player, enemyDamage)
                    line("battle")

                skillCooldownTrack(player)
                battleLog(f"{player.name} Health: {player.health}/{player.maxHealth}")
                battleLog(f"{player.name} Mana: {player.mana}/{player.maxMana}")
                battleLog(f"{enemy.name} Health: {enemy.health}/{enemy.maxHealth}")
                battleLog(f"Action: {actions} ")
                battleLog("##------------===------------##\n")
                if player.sanity > 0:
                    player.sanity -= 1
                elif player.sanity < 0:
                    player.sanity += 1
                # Speed Meter Reset
                player.speedMeter -= 100
                player.wasHit = False
                lastActor = "player"
                input("?>")

            if enemy.speedMeter >= 100 and (enemy.health > 0 or any(s.name == "Phoenix Blessing" for s in enemy.statusList)):
                actions += 1
                result = actionTime("enemy", enemy, player, battleType, theme)
                line("battle")
                
                if result:
                    if enemy.lastAction and enemy.lastAction == "Skill" and enemy.lastSkill and "Damage" in enemy.lastSkill.type_:
                        if lastActor == "enemy":
                            enemyDamage += result
                        else:
                            enemyDamage = result
                if theme:
                    print("Theme Effect:")
                    themeEffects(theme, enemy, player, actions, "enemy")
                    line("battle")

                if sum(1 for s in enemy.skills if "Passive" in s.type_) > 0:
                    print("Passive Effects:")
                    passiveEffects(player, enemy, "enemy", result)
                    line("battle")

                if len(player.sigils) > 0:
                    print("Sigil Effects:")
                    sigilEffects(player, enemy, "afterEnemyAction", result=result)
                    line("battle")
                
                if len(enemy.statusList) > 0:
                    print("Status Effects:")
                    statusDurationTracker("enemy", enemy, player, playerDamage)
                    line("battle")

                battleLog(f"{player.name} Health: {player.health}/{player.maxHealth}")
                battleLog(f"{player.name} Mana: {player.mana}/{player.maxMana}")
                battleLog(f"{enemy.name} Health: {enemy.health}/{enemy.maxHealth}")
                battleLog(f"Action: {actions} ")
                battleLog("##------------===------------##\n")
                if enemy.sanity < 0:
                    enemy.sanity += 1
                if enemy.sanity > 0:
                    enemy.sanity -= 1
                # Speed Meter Reset
                enemy.speedMeter -= 100
                enemy.wasHit = False
                lastActor = "enemy"
                input("?>")

            # Transformations
            if enemy.canTransform and enemy.transTrigger(enemy, player):
                line("battle")
                enemy.transform(player)
                line("battle")
                input("!>")
                clear()

            # Health Check
            if ((player.health <= 0 and not any(s.name == "Phoenix Blessing" for s in player.statusList)) or timed and actions > limit) and battle:
                clear()
                line("battle")
                say(f"{Color['red']}Enemy Won!{Color['reset']}")
                line("battle")
                input("?>")
                
                resetBattleState(player)
                resetBattleState(enemy)
                enemy.ultimateMeter = 0
                
                if battleType in ["Boss Map/Main", "Extreme"]:
                    clear()
                    
                    line("basic")
                    print(f"{Color['red']}Retry?{Color['reset']}")
                    line("basicOther")
                    
                    print(f"1. {Color['green']}Yes{Color['reset']} | 2. {Color['red']}No{Color['reset']}")
                    
                    while True:
                        choice = input("?>")
                        
                        if choice == "1":
                            RETRY = True
                            battle = False
                            time.sleep(0.5)
                            break
                        
                        elif choice == "2":
                            break

                battleLogFile = None
                if not RETRY:
                    outer = False
                    return "Loss"
                else:
                    break
                
            if (enemy.health <= 0 and not any(s.name == "Phoenix Blessing" for s in enemy.statusList))and battle:
                clear()
                
                line("basic")
                say("Player Won!")
                line("basic")

                if not specialBattle: 
                    if battleType in ["Raid Normal", "Raid Boss"]:
                        luckBonus = min(0.25, player.luck * 0.002)
                        
                        coinReward = round(enemy.coin + random.randint(1, 5) * (1 + luckBonus))
                        gpReward = round(enemy.maxHealth * 0.25 * 5 * (1 + luckBonus))
                        expReward = round(enemy.exp + random.randint(1, 5) * (1 + luckBonus))
                        
                        statusRewards(player, coinReward, gpReward)
                        
                        print(f"{Color['yellow']}{player.name} Got {coinReward} Coins!{Color['reset']}")
                        print(f"{Color['cyan']}{player.name} Got {gpReward} GP!{Color['reset']}")
                        print(f"{Color['cyan']}{player.name} Got {expReward} EXP!{Color['reset']}")
                        player.coins += coinReward
                        player.gamePoints += gpReward
                        player.levelValue += expReward

                    manaBefore = player.mana
                    player.mana = min(player.maxMana, player.mana + round(player.sigillessMaxMana * 0.15) + random.randint(1, 2))
                    manaRestored = player.mana - manaBefore
                    print(f"{Color['blue']}{manaRestored} Mana Restored!{Color['reset']}")
                    line("basicOther")

                    say(f"Actions: {actions}")
                    line("basicOther")

                    input("?>")
                clear()

                battleLogFile = None
                resetBattleState(player, "Survival" if battleType == "Survival" else None)
                resetBattleState(enemy)
                enemy.ultimateMeter = 0

                outer = False
                return "Win"
            
            if keyboard.is_pressed("shift"):
                if not SHIFT:
                    SPEED = not SPEED
                    SHIFT = True
                    if SPEED:
                        print(f"{Color['yellow']}>> Speed Mode On!{Color['reset']}")
                    else:
                        print(f"{Color['yellow']}>> Speed Mode Off!{Color['reset']}")
                    time.sleep(0.2)
            else:
                SHIFT = False
            if SPEED:
                time.sleep(0.2)
            else:
                time.sleep(0.4)
        clear()
initBattle(battleLoop)