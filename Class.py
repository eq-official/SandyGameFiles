from Utility import *

# Never Mind! Found The Best Way To Handle This! \_^-^_/
battleLoopFunc = None
def initBattle(func):
    global battleLoopFunc
    battleLoopFunc = func

def statusInText(name, text):
    return bool(re.search(r'(?<![A-Za-z])' + re.escape(name) + r'(?![A-Za-z0-9])', text))

def printStatus(status, skill, shown):
    if not statusInText(status.name, skill.text if isinstance(skill, (Skill, BuddySkill)) else skill.effect):
        return
    if status.name in shown:
        return
    if status.name.endswith(" I"):
        higher = status.name[:-1] + "II"
        if higher in shown:
            return
    
    shown.add(status.name)
    print(f"{(Color['green'] if status.align == "Positive" else Color['red'] if status.align == "Negative" else Color['yellow']) + Color['line']}{status.name}{Color['reset']}: {status.text}")
    
    for other in Status.allStatuses.values():
        if other.name not in shown and statusInText(other.name, status.text):
            printStatus(other, skill, shown)

##------------===------------##

class Player:
    def __init__(self, name, playerClass, health, mana, strength, magic, defense, resistance, luck, hit, speed, skills):
        self.name = name
        self.actions = 0
        self.level = 1
        self.levelGoal = 40
        self.levelValue = 0
        self.playerClass = playerClass
        self.health = health
        self.maxHealth = self.health
        self.mana = mana
        self.maxMana = self.mana
        
        self.sanity = 0

        # Used Stats
        self.strength = strength
        self.magic = magic
        self.defense = defense
        self.resistance = resistance
        self.luck = luck
        self.hit = hit
        self.speed = speed

        # Unmutated Stats 
        self.baseMaxHealth = self.maxHealth
        self.baseMaxMana = self.maxMana
        self.baseStrength = self.strength
        self.baseMagic = self.magic
        self.baseDefense = self.defense
        self.baseResistance = self.resistance
        self.baseLuck = self.luck
        self.baseHit = self.hit
        self.baseSpeed = self.speed

        # sigilless Stats:
        self.sigillessMaxHealth = self.maxHealth
        self.sigillessMaxMana = self.maxMana
        self.sigillessStrength = self.strength
        self.sigillessMagic = self.magic
        self.sigillessDefense = self.defense
        self.sigillessResistance = self.resistance
        self.sigillessLuck = self.luck
        self.sigillessHit = self.hit
        self.sigillessSpeed = self.speed

        self.speedMeter = 0
        self.skills = skills
        self.reserveSkills = []
        self.sigils = []
        self.reserveSigils = []
        self.buddy = None
        self.reserveBuddies = []
        self.items = []
        self.itemStorage = []
        self.statusList = []
        self.coins = 0
        self.gamePoints = 0
        self.modifiers = []
        self.vit = 0
        self.bdy = 0
        self.utl = 0
        self.x = 3
        self.y = 3
        self.location = "None"
        self.savedMaps = {}
        self.builds = {}
        self.travelLog = []
        self.battleTriggers = []
        self.logs = True
        self.lastSkill: PlayerSkill = None
        self.attackHits = 0
        self.lastItem = None
        self.lastAction = None
        self.wasHit = False
    
    def attack(self, user, target, actions):
        user.lastAction = "Attack"
        say(f"{user.name} Attacked!")
        damage = 0
        
        if user.hit + random.randint(10,30) >= random.randint(1, 80) + round(target.luck * 0.25):
            shield = False if not any(s.name == "Health Shield" for s in target.statusList) else True
            
            damage = max(0, (user.strength if user.strength >= user.magic else user.magic) + random.randint(1, 5) - ((target.defense if user.strength >= user.magic else target.resistance) // 2))
            
            if user.luck >= random.randint(1, 200) + target.luck:
                damage *= 2
                say(f"{Color['yellow']}Critical Strike!{Color['reset']}")
            
            for status in user.statusList[:]: 
                if callable(status.damageInterupt):
                    damage = status.damageInterupt(user, target, damage, "user")
    
            for status in target.statusList[:]: 
                if callable(status.damageInterupt):
                    damage = status.damageInterupt(target, user, damage, "target")     
            
            if not target.wasHit:
                user.attackHits = 1
            else: user.attackHits += 1
            
            if not shield:                    
                say(f"{Color['red']}{user.name} Dealt {damage} Damage To {target.name}!{Color['reset']}")
                target.health -= damage
                target.wasHit = True
            
            else:
                say(f"{Color['cyan']}{target.name}s Health Shield Blocked The Damage! Health Shield Lost {user.attackHits} Stacks!{Color['reset']}")
                next(s for s in target.statusList if s.name == "Health Shield").stacks -= user.attackHits
                damage = 0
                
        else:
            say("The Attack Missed!")
            user.lastAction = "Miss"
            return None

        if user.buddy:
            buddy = user.buddy
            if buddy.talent + random.randint(1, 65) > 100 and not any(s.name == "Health Shield" for s in target.statusList):
                say(f"{Color['cyan']}Buddy Strike!{Color['reset']}")
                
                dam = max(0, buddy.attack * 2 - (target.defense if target.defense >= target.resistance else target.resistance) // 2)
                
                if buddy.talent + random.randint(1, 25) >= random.randint(1, 50) + round(target.luck * 0.50):
                    dam = round(dam * 1.5)
                    say(f"{Color['yellow']}Critical Strike!{Color['reset']}")
                    
                say(f"{Color['red']}{buddy.name} Dealt {dam} Damage To {target.name}!{Color['reset']}")
                target.health -= dam
        
        return damage

    def wait(self, user, target, actions):
        user.lastAction = "Wait"
        say(f"{user.name} Waited!")
            
        # Health Regen
        if user.health < user.maxHealth * 0.75:
            heal = round(user.maxHealth * 0.08) + random.randint(1, 6)
            user.health += heal
            say(f"{Color['green']}{user.name}s Health Was Restored By {heal}!{Color['reset']}")
        
        # Mana Regen
        if user.mana < user.maxMana * 0.50:
            heal = round(user.maxMana * 0.15) + random.randint(1, 5)
            user.mana += heal
            say(f"{Color['green']}{user.name}s Mana Was Restored By {heal}!{Color['reset']}")
            
        # Status Cleanse
        if len(user.statusList) > 0:
            for status in user.statusList[:]:
                if status.align == "Negative" and random.randint(1, 100) >= 75:
                    status.duration = status.maxDuration 
                    say(f"{Color['green']}{user.name} No Longer Has {status.name}!{Color['reset']}")
                    break
        
        user.sanity += 3
    
    def analyze(self, enemy, theme):
        clear()

        print(f"Information")
        line("analyze")
        
        if theme:
            print(theme)
            line("analyze")
            print("")

        meter = ""
        total = min(20, enemy.maxHealth // 10)
        filled = min(total, enemy.health // 10)
        filled = max(0, filled)
        meter = f"{Color['red']}▮{Color['reset']}" * filled + "▯" * (total - filled)

        print(f"{enemy.name} Health: {meter}")
        print(f"Health: {Color['red']}{enemy.health}/{enemy.maxHealth}{Color['reset']}")
        print(f"Strength: {Color['cyan']}{enemy.strength}{Color['reset']} | Magic: {Color['cyan']}{enemy.magic}{Color['reset']}")
        print(f"Defense: {Color['cyan']}{enemy.defense}{Color['reset']} | Resistance: {Color['cyan']}{enemy.resistance}{Color['reset']}")
        print(f"Luck: {Color['yellow']}{enemy.luck}{Color['reset']} | Hit: {Color['yellow']}{enemy.hit}{Color['reset']} | Speed: {Color['yellow']}{enemy.speed}{Color['reset']}")
        print(f"Statuses: {Color['green']}{', '.join(f'{s.name} ({s.duration}/{s.maxDuration})' + (f' [{s.stacks}/{s.maxStack}]' if s.canStack else '') for s in enemy.statusList) or 'None'}{Color['reset']}")
        print(f"F: {elements['fire'].get(enemy.fire)} | I: {elements['ice'].get(enemy.ice)} | T: {elements['thunder'].get(enemy.thunder)} | W: {elements['wind'].get(enemy.wind)}| M: {elements['mighty'].get(enemy.mighty)} | P: {elements['physical'].get(enemy.physical)}")
        line("analyze")
        
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
        print("Sanity Meter: " + meter)
        line("analyze")

        # Speed Meter
        meter = ""
        for i in range(0, 100, 10):
            if enemy.speedMeter > i:
                meter += f"{Color['yellow']}▮{Color['reset']}>"
            else:
                meter += f"{Color['yellow']}▯{Color['reset']}>"
        meter = "-" + meter
        print("Action Meter: " + meter) 
        line("analyze")
        print("")
        
        # Enemy Skills
        print("Skills")
        line("analyze")
        
        number = 1
        for skill in enemy.skills:
            print(f"{number}. {Color['red']}{skill.name}{' | ' + skill.sanLean if "Damage" in skill.type_ else ''} | Hit: {skill.hit if skill.hit > 0 else '-'} | Critical: {skill.critical if skill.critical > 0 else '-'}{Color['reset']}")
            text = Color['yellow'] + skill.text + Color['reset']
            names = sorted(Status.allStatuses.keys(), key=len, reverse=True)
            pattern = r"\b(" + "|".join(map(re.escape, names)) + r")\b"
            text = re.sub(pattern, lambda m: colorize(m, Status), text)
            print(text)
            
            shown = set()
            for s in Status.allStatuses.values():
                printStatus(s, skill, shown)
            line("analyze")      
        print("")  

        # Ultimate Meter/Skill(s)
        meter = ""
        for i in range(0, 70, 10):
            if enemy.ultimateMeter > i:
                meter += f"{Color['magenta']}▮{Color['reset']}!"
            else:
                meter += f"{Color['magenta']}▯{Color['reset']}!"
        willTrigger = f"{Color['green']}Ready{Color['reset']}" if enemy.ultimateMeter >= 70 else f"{Color['red']}Charging{Color['reset']}"
        meter = "-" + meter + f" | {enemy.ultimateMeter}/70" + " | Status: " + willTrigger
        print("Ultimate Meter: " + meter)
        line("analyze")
                
        if not isinstance(enemy.ultimateSkill, list):
            print(f"Ultimate Skill:\n{Color['red']}{enemy.ultimateSkill.name}{' | ' + enemy.ultimateSkill.sanLean if "Damage" in enemy.ultimateSkill.type_ else ''} | Hit: {enemy.ultimateSkill.hit if enemy.ultimateSkill.hit > 0 else '-'} | Critical: {enemy.ultimateSkill.critical if enemy.ultimateSkill.critical > 0 else '-'}{Color['reset']}")
            text = Color['yellow'] + enemy.ultimateSkill.text + Color['reset']
            names = sorted(Status.allStatuses.keys(), key=len, reverse=True)
            pattern = r"\b(" + "|".join(map(re.escape, names)) + r")\b"
            text = re.sub(pattern, lambda m: colorize(m, Status), text)
            print(text)
            shown = set()
            for s in Status.allStatuses.values():
                printStatus(s, enemy.ultimateSkill, shown)
            line("analyze")  
        else:
            number = 1
            for ult in enemy.ultimateSkill:
                print(f"{number}. {Color['red']}{ult.name}{' | ' + ult.sanLean if "Damage" in ult.type_ else ''} | Hit: {ult.hit if ult.hit > 0 else '-'} | Critical: {ult.critical if ult.critical > 0 else '-'}{Color['reset']}")
                text = Color['yellow'] + ult.text + Color['reset']
                names = sorted(Status.allStatuses.keys(), key=len, reverse=True)
                pattern = r"\b(" + "|".join(map(re.escape, names)) + r")\b"
                text = re.sub(pattern, lambda m: colorize(m, Status), text)
                print(text)
                shown = set()
                for s in Status.allStatuses.values():
                    printStatus(s, enemy.ultimateSkill, shown)
                line("analyze")  
                number += 1
        print("")  

        # Buddy Meter
        if self.buddy:
            meter = ""
            for i in range(0, 150, 10):
                if self.buddy.buddyMeter > i:
                    meter += f"{Color['cyan']}▮{Color['reset']}!"
                else:
                    meter += f"{Color['cyan']}▯{Color['reset']}!"
            willTrigger = f"{Color['green']}Ready{Color['reset']}" if self.buddy.buddyMeter >= 150 else f"{Color['red']}Charging{Color['reset']}"
            meter = "-" + meter + f" | {self.buddy.buddyMeter}/150" + " | Status: " + willTrigger 
            print("Buddy Meter: " + meter)
            line("analyze")
            
            print(f"{self.buddy.name} {Color['reset']}|{Color['cyan']} {self.buddy.affinity}")
            print(f"{Color['cyan']}Attack: {self.buddy.attack} {Color['reset']}|{Color['cyan']} Talent: {self.buddy.talent} {Color['reset']}|{Color['cyan']} Speed: {self.buddy.speed}{Color['reset']}")
            text = Color['yellow'] + self.buddy.passive.text + Color['reset']
            names = sorted(Status.allStatuses.keys(), key=len, reverse=True)
            pattern = r"\b(" + "|".join(map(re.escape, names)) + r")\b"
            text = re.sub(pattern, lambda m: colorize(m, Status), text)
            print(f"{Color['cyan']}{self.buddy.passive.name}{Color['reset']}: {text}")
            
            shown = set()
            for s in Status.allStatuses.values():
                printStatus(s, self.buddy.passive, shown)
            
            text = Color['yellow'] + self.buddy.skill.text + Color['reset']
            names = sorted(Status.allStatuses.keys(), key=len, reverse=True)
            pattern = r"\b(" + "|".join(map(re.escape, names)) + r")\b"
            text = re.sub(pattern, lambda m: colorize(m, Status), text)
            print(f"{Color['cyan']}{self.buddy.skill.name}{Color['reset']}: {text} {f'| {Color['yellow']} Hit: {self.buddy.skill.hit} {Color['reset']} | {Color['yellow']} Critical: {self.buddy.skill.critical}' if 'Damage' in self.buddy.skill.type_ else ''} {Color['reset']}")
            
            shown = set()
            for s in Status.allStatuses.values():
                printStatus(s, self.buddy.skill, shown)
            print("")
        
        print(f"{enemy.name} Statuses")
        line("analyze")  

        for status in enemy.statusList:
            color = Color['green' if status.align == 'Positive' else 'red' if status.align == 'Negative' else 'yellow']
            print(f"{status.name}| Duration: {status.duration}/{status.maxDuration if not status.forever else '∞'} | Stacks: {f'{status.stacks}/{status.maxStack}' if status.canStack else 'N/A'} | {f'Count: {status.count}' if hasattr(status, 'count') else 'N/A'}")
            print(f"{color}{status.text}{Color['reset']}")
            line("analyze")  
        print("")

        print(f"{self.name} Statuses")
        line("analyze")  
        for status in self.statusList:
            color = Color['green' if status.align == 'Positive' else 'red' if status.align == 'Negative' else 'yellow']
            print(f"{status.name} | Duration: {status.duration}/{status.maxDuration if not status.forever else '∞'} | Stacks: {f'{status.stacks}/{status.maxStack}' if status.canStack else 'N/A'} | {f'Count: {status.count}' if hasattr(status, 'count') else 'N/A'}")
            print(f"{color}{status.text}{Color['reset']}")
            line("analyze")  

        input("?>")

class Enemy:
    allEnemies = {}

    def __init__(self, name, personality, health, strength, magic, defense, resistance, luck, hit, speed, skills, favoredSkill, ultimateSkill, affnities, coin, exp, canTransform=False, transformTo=None, transTrigger=None, theme=None):
        self.name = name
        self.actions = 0
        self.personality = personality # Tactical/Opportunist/Aggressive/Cowardly/Sadistic/Honorable
        self.health = health() if callable(health) else health
        self.maxHealth = self.health
        self.theme = theme
        self.lastSkill: EnemySkill = None
        self.attackHits = 0
        self.lastAction = None
        self.wasHit = False

        self.sanity = 0

        # Transforming Enemies
        self.transformTo = transformTo
        self.canTransform = canTransform
        self.transTrigger = transTrigger

        # Used Stats
        self.strength = strength
        self.magic = magic
        self.defense = defense
        self.resistance = resistance
        self.luck = luck
        self.hit = hit
        self.speed = speed

        # Unmutated Stats
        self.baseStrength = self.strength
        self.baseMagic = self.magic
        self.baseDefense = self.defense
        self.baseResistance = self.resistance
        self.baseLuck = self.luck
        self.baseHit = self.hit
        self.baseSpeed = self.speed

        self.speedMeter = 0

        self.skills = skills
        self.favoredSkill = favoredSkill
        self.ultimateSkill = ultimateSkill
        self.ultimateMeter = 0
        self.statusList = []

        self.coin = coin
        self.exp = exp

        self.fire = affnities[0]
        self.ice = affnities[1]
        self.thunder = affnities[2]
        self.wind = affnities[3]
        self.mighty = affnities[4]
        self.physical = affnities[5]

        Enemy.allEnemies[self.name] = self

    def attack(self, user, target, actions):
        user.lastAction = "Attack"
        say(f"{user.name} Attacked!")
        
        if user.hit + random.randint(10,30) >= random.randint(1, 80) + round(target.luck * 0.25):
            shield = False if not any(s.name == "Health Shield" for s in target.statusList) else True
            
            damage = max(0, (user.strength if user.strength >= user.magic else user.magic) + random.randint(1, 5) - ((target.defense if user.strength >= user.magic else target.resistance) // 2))
            
            if user.luck >= random.randint(1, 200) + target.luck:
                damage *= 2
                say(f"{Color['yellow']}Critical Strike!{Color['reset']}")
                
            for status in user.statusList[:]: 
                if callable(status.damageInterupt):
                    damage = status.damageInterupt(user, target, damage, "user")
    
            for status in target.statusList[:]: 
                if callable(status.damageInterupt):
                    damage = status.damageInterupt(target, user, damage, "target")    
            
            if not target.wasHit:
                user.attackHits = 1
            else: user.attackHits += 1
            
            if not shield:                    
                say(f"{Color['red']}{user.name} Dealt {damage} Damage To {target.name}!{Color['reset']}")
                target.health -= damage
                target.wasHit = True
                return damage
            
            else:
                say(f"{Color['cyan']}{target.name}s Health Shield Blocked The Damage! Health Shield Lost {user.attackHits} Stacks!{Color['reset']}")
                next(s for s in target.statusList if s.name == "Health Shield").stacks -= user.attackHits
                damage = 0
                return damage

        else:
            say("The Attack Missed!")
            user.lastAction = "Miss"
            return None

    def wait(self, user, target, actions):
        user.lastAction = "Wait"
        say(f"{user.name} Waited!")
            
        # Health Regen
        if user.health < user.maxHealth * 0.60:
            heal = round(user.maxHealth * 0.15) + random.randint(1, 6)
            user.health += heal
            say(f"{Color['green']}{user.name} Healed By {heal}!{Color['reset']}")
        
        # Status Cleanse
        if len(user.statusList) > 0:
            for status in user.statusList[:]:
                if status.align == "Negative" and random.randint(1, 100) >= 75:
                    status.duration = status.maxDuration 
                    say(f"{Color['green']}{user.name} No Longer Has {status.name}!{Color['reset']}")
                    break
        
        user.sanity += 3

    def behavior(self, enemy, target, actions=1):
        def allowed(skill):
            return skill.weightConditional is None or skill.weightConditional(enemy, target, actions)
        
        weights = {enemy.attack: 11, enemy.wait: 3}

        if actions == 1:
            weights[enemy.wait] = 0
            weights[enemy.attack] = 0

        for skill in enemy.skills:
            if "Passive" in skill.type_:
                continue
            if allowed(skill):
                weights[skill.effect] = skill.weight
            else:
                continue
                
            if callable(skill.condition) and skill.condition(enemy, target):
                weights[skill.effect] *= 2

            if actions == 1 and skill.opener:
                weights[skill.effect] += 15
            
            if target.health <= round(target.maxHealth * 0.25) and skill.finisher:
                weights[skill.effect] += 20

            for status in target.statusList:
                if status.taunt and "Damage" in skill.type_:
                    weights[skill.effect] += status.taunt

        negatives = 0
        for status in enemy.statusList:
            if status.align == "Negative":
                negatives += 1
        if negatives >= 3: weights[enemy.wait] += 5
    
        # Personalitys
        if enemy.personality == "Tactical":
            if enemy.favoredSkill.effect in weights:
                weights[enemy.favoredSkill.effect] += enemy.favoredSkill.weight

            if actions > 10:
                for skill in enemy.skills:
                    if "Passive" in skill.type_ or skill.effect not in weights:
                        continue
                    weights[skill.effect] += skill.weight

        elif enemy.personality == "Opportunist":
            if target.health <= round(target.maxHealth * 0.50):
                for skill in enemy.skills:
                    if "Passive" in skill.type_ or skill.effect not in weights:
                        continue
                    if "Damage" in skill.type_:
                        weights[skill.effect] += skill.weight
            
            if enemy.speed > target.speed:
                for skill in enemy.skills:
                    if "Passive" in skill.type_ or skill.effect not in weights:
                        continue
                    weights[skill.effect] += skill.weight

        elif enemy.personality == "Aggressive":
            for skill in enemy.skills:
                if "Passive" in skill.type_ or skill.effect not in weights:
                        continue
                weights[skill.effect] += 10

            if enemy.health < round(enemy.maxHealth * 0.45):
                for skill in enemy.skills:
                    if "Passive" in skill.type_ or skill.effect not in weights:
                        continue
                    if "Damage" in skill.type_:
                        weights[skill.effect] += skill.weight
        
        elif enemy.personality == "Cowardly":
            if enemy.health > round(enemy.maxHealth * 0.75):
                weights[enemy.wait] += 20
                
            else:
                for skill in enemy.skills:
                    if "Passive" in skill.type_ or skill.effect not in weights:
                        continue
                    if "Damage" in skill.type_:
                        weights[skill.effect] += 10
                   
        elif enemy.personality == "Sadistic":
            if any(s.align == "Negative" for s in target.statusList):
                for skill in enemy.skills:
                    if "Passive" in skill.type_ or skill.effect not in weights:
                        continue
                    weights[skill.effect] += 8

            for skill in enemy.skills:
                    if "Passive" in skill.type_ or skill.effect not in weights:
                        continue
                    if "Damage" in skill.type_:
                        weights[skill.effect] += 5
        
        elif enemy.personality == "Honorable":
            if target.health <= round(target.maxHealth * 0.50):
                for skill in enemy.skills:
                    if "Passive" in skill.type_ or skill.effect not in weights:
                        continue
                    weights[skill.effect] -= 5
            
            if target.health >= round(target.maxHealth * 0.50):
                for skill in enemy.skills:
                    if "Passive" in skill.type_ or skill.effect not in weights:
                        continue
                    if "Damage" in skill.type_:
                        weights[skill.effect] += skill.weight
        
        action = random.choices(list(weights.keys()), weights= [weights[w] for w in weights])[0]
        return action(enemy, target, actions)

    def transform(self, target):
        if self.canTransform:
            if self.transTrigger(self, target):
                newForm = copy.deepcopy(self.transformTo)
                
                # Transformation
                oldName = self.name
                self.name = newForm.name

                self.strength = newForm.strength
                self.magic = newForm.magic
                self.defense = newForm.defense
                self.resistance = newForm.resistance
                self.luck = newForm.luck
                self.hit = newForm.hit
                self.speed = newForm.speed

                self.baseStrength = newForm.baseStrength
                self.baseMagic = newForm.baseMagic
                self.baseDefense = newForm.baseDefense
                self.baseResistance = newForm.baseResistance
                self.baseLuck = newForm.baseLuck
                self.baseHit = newForm.baseHit
                self.baseSpeed = newForm.baseSpeed

                for skill in self.skills:
                    if hasattr(skill, "tag"):
                        newForm.skills.append(copy.deepcopy(skill))
                self.skills = newForm.skills
                self.personality = newForm.personality
                self.ultimateSkill = newForm.ultimateSkill

                self.maxHealth = newForm.maxHealth
                self.health = self.maxHealth
                self.coin = newForm.coin
                self.exp = newForm.exp
                self.theme = newForm.theme
                self.sanity = 0
                self.statusList = [s for s in self.statusList if s.align != "Negative"]
                
                for item in ["fire", "ice", "thunder", "wind", "mighty", "physical"]:
                    setattr(self, item, getattr(newForm, item))

                self.canTransform = newForm.canTransform
                self.transformTo = newForm.transformTo
                self.transTrigger = newForm.transTrigger
                say(f"{Color['red']}{oldName} Transformed!{Color['reset']}")

class Status:
    allStatuses = {}

    def __init__(self, name, family, maxDuration, type_, align, text, meter="health", canStack=False, maxStack=1, stackScale=1, damage=None, mutate=[], chanceToProlong=55, prolong=1, noCoexist=None, transform=False, counter=None, counterType="damage", counterDamage=None, healWho = "enemy", sanity=0, sanityCondition=True, shift=None, scaleWithStacks=True, forever=False, taunt=None):
        self.name = name
        self.family = family # Groups Are: Burn, Chill, Shock, Bleed, Poison, Mental, Other
        self.text = text
        self.type_ = type_ # Damage, Debuff, Buff, Prolonger, Special
        self.align = align # Negative Or Positive
        self.duration = 0
        self.maxDuration = maxDuration # Will Remove Whole Status/Stack Once duration Reaches maxDuration
        self.meter = meter
        self.stacks = 0
        self.scaleWithStacks = scaleWithStacks
        self.canStack = canStack # If False, Will Not Stack On New Infliction, Else True Will Stack On New Infliction
        self.maxStack = maxStack # Will Remove One Stack When Duration Reaches maxDuration
        self.stackScale = stackScale # Default Is 1. Used For Buffing/Debuffing Statuses
        self.damage = damage # [[(stat_one, percent), (stat_two, percent), etc], random flat bonus, multiplier] 
        self.mutate = mutate #[(stat_one, -5) (stat_two, 3)] - For Debuffs, nothing for Buffs
        self.counter = counter # [multiplier, flatAmount] | [multiplier, stat]
        self.counterType = counterType # damage/self
        self.counterDamage = counterDamage # physical/magic
        self.chanceToProlong = chanceToProlong
        self.prolong = prolong # Used by Prolonger statuses
        self.transform = transform # Transform At Max Stack/End of Duration
        self.healWho = healWho
        self.sanity = sanity
        self.sanityCondition = sanityCondition
        self.shift = shift
        self.noCoexist = noCoexist
        self.forever = forever
        self.taunt = taunt
        Status.allStatuses[self.name] = self
    
    def inflict(self, target, stacks=1, count=1):
        existing = next((s for s in target.statusList if s.name == self.name), None)
        if existing:
            if existing.canStack:
                if existing.stacks < existing.maxStack:
                    gainedStacks = min(stacks, existing.maxStack - existing.stacks)
                    existing.stacks = min(existing.maxStack, existing.stacks + stacks)
                    
                    if "Debuff" in existing.type_ or "Buff" in existing.type_:
                        existing.statMutation(target)

                    if stacks > 0:
                        say(f"{Color['green']}{target.name} Gained {gainedStacks} {'Stacks' if gainedStacks > 1 else 'Stack'} Of {self.name}!{Color['reset']}")
                    
                    if hasattr(self, "count"):
                        say(f"{Color['green']}{target.name} Gained {count} Count Of {self.name}!{Color['reset']}")
                        existing.count += count

        else:
            say(f"{Color['green']}{target.name} Was Inflicted With {self.name}!{Color['reset']}")
            newStatus = copy.deepcopy(self)
            if "Shift" in newStatus.type_:
                newStatus.simple(target, newStatus.meter)
            if self.canStack:
                newStatus.stacks += stacks
            if hasattr(self, "count"):
                newStatus.count = count
            newStatus.coexistCheck(target)
            target.statusList.append(newStatus)

            if "Debuff" in newStatus.type_ or "Buff" in newStatus.type_:
                newStatus.statMutation(target)

    def remove(self, target, stacks=1, count=0, full=False):
        existing = next((s for s in target.statusList if s.name == self.name), None)
        if existing:
            if existing.canStack and not full:
                removed = min(stacks, existing.stacks)
                existing.stacks = max(0, existing.stacks - stacks)

                if existing.stacks <= 0:
                    target.statusList.remove(existing)

                if "Debuff" in existing.type_ or "Buff" in existing.type_:
                    existing.statMutation(target)

                if removed > 0:
                    say(f"{Color['green']}{target.name} Lost {removed} {'Stacks' if removed > 1 else 'Stack'} Of {self.name}!{Color['reset']}")

                if hasattr(self, "count") and count > 0:
                    say(f"{Color['green']}{target.name} Lost {count} Count Of {self.name}!{Color['reset']}")
                    existing.count -= count
                    if existing.count <= 0:
                        existing.count = 0

            else:
                say(f"{Color['green']}{target.name} Lost {self.name}!{Color['reset']}")
                target.statusList.remove(existing)

    def statMutation(self, target):
        number = 0

        # Reset Targets Stats To Base
        for stat in ["strength", "magic", "defense", "resistance", "luck", "hit", "speed", "maxHealth", "maxMana"]:
            if isinstance(target, Player):
                if stat == "maxHealth":
                    setattr(target, stat, getattr(target, f"sigillessMaxHealth"))
                    continue
                elif stat == "maxMana":
                    setattr(target, stat, getattr(target, f"sigillessMaxMana"))
                    continue
                setattr(target, stat, getattr(target, f"sigilless{stat.capitalize()}"))

            else:
                if stat in ["maxHealth", "maxMana"]:
                    continue
                setattr(target, stat, getattr(target, f"base{stat.capitalize()}"))

        for status in target.statusList:
            if len(status.mutate) == 0: continue

            for setS in status.mutate:
                if status.canStack == True and status.scaleWithStacks == True:
                    if status.stacks > 0:
                        stack = status.stacks

                        if setS[1] < 0:
                            number = setS[1] - (stack * status.stackScale)
                            setattr(target, setS[0], getattr(target, setS[0]) + number)
                        elif setS[1] > 0:
                            number = setS[1] + (stack * status.stackScale)
                            setattr(target, setS[0], getattr(target, setS[0]) + number)
                else:
                    number = setS[1]
                    setattr(target, setS[0], getattr(target, setS[0]) + number)
        
        for stat in ["strength", "magic", "defense", "resistance", "luck", "hit", "speed"]:
            if stat != "speed":
                setattr(target, stat, max(1, getattr(target, stat)))
            
            else:
                setattr(target, stat, max(5, getattr(target, stat)))
        
        if hasattr(target, "sigils"):
            for sigil in target.sigils:
                for stat, amount in sigil.statChange:
                    setattr(target, stat, getattr(target, stat) + amount)

        return number

    def turnIncrement(self, target):
        self.duration += 1
        if not self.forever:
            if self.duration >= self.maxDuration:
                if self.canStack == True and self.stacks > 1:
                    self.stacks -= 1
                    self.duration = 0
                    if "Debuff" in self.type_ or "Buff" in self.type_:
                        self.statMutation(target)
                
                else:
                    self.remove(target, full=True)
                    if self.transform and not self.canStack:
                        self.transform.inflict(target)
                    if "Debuff" in self.type_ or "Buff" in self.type_:
                        self.statMutation(target)

                    if "Shift" in self.type_:
                        for element in ["fire", "ice", "wind", "thunder", "mighty", "physical"]:
                            setattr(target, element, getattr(Enemy.allEnemies[target.name], element))
            
            if self.duration < 0:
                self.duration = 0

            if self.canStack and self.stacks >= self.maxStack and self.transform:
                self.transform.inflict(target)

                if self in target.statusList:
                    self.remove(target, full=True)

    # Damage, Debuff, Buff
    def simple(self, target, damage=0, enemy=None):
        preDamage = damage
        heal = 0
        
        if "Damage" in self.type_ and not "Special" in self.type_:
            flatDamage = self.damage[1]() if callable(self.damage[1]) else self.damage[1]

            numbersList = []
            for stat, percent in self.damage[0]:
                numbersList.append(percent / 100 * getattr(target, stat))

            damage = 0
            for number in numbersList:
                damage += number

            if self.canStack == True:
                damage = round(damage * self.damage[2]) + flatDamage * self.stacks
            else:
                damage = round(damage * self.damage[2]) + flatDamage


            if hasattr(target, self.meter):
                setattr(target, self.meter, getattr(target, self.meter) - damage)
                if getattr(target, self.meter) < 0:
                    setattr(target, self.meter, 0)
                say(f"{Color['red']}{target.name} Took {damage} {self.meter.capitalize()} Damage From {self.name}!{Color['reset']}")

        if "Heal" in self.type_ and not "Special" in self.type_:
            flatHeal = self.damage[1]() if callable(self.damage[1]) else self.damage[1]

            numbersList = []
            for stat, percent in self.damage[0]:
                if hasattr(target, stat):
                    numbersList.append(percent / 100 * getattr(target, stat))

            heal = 0
            for number in numbersList:
                heal += number

            if self.canStack == True:
                heal = round(heal * self.damage[2]) + flatHeal * self.stacks
            else:
                heal = round(heal * self.damage[2]) + flatHeal

            if self.healWho == "enemy":
                if hasattr(enemy, self.meter):
                    setattr(enemy, self.meter, getattr(enemy, self.meter) + heal)
                    if getattr(enemy, self.meter) < 0:
                        setattr(enemy, self.meter, 0)
                    say(f"{Color['green']}{enemy.name}s {self.meter.capitalize()} Was Restored By {heal} From {self.name}!{Color['reset']}")

            elif self.healWho == "target":
                if hasattr(target, self.meter):
                    setattr(target, self.meter, getattr(target, self.meter) + heal)
                    if getattr(target, self.meter) < 0:
                        setattr(target, self.meter, 0)
                    say(f"{Color['green']}{target.name}s {self.meter.capitalize()} Was Restored By {heal} From {self.name}!{Color['reset']}")

        if ("Debuff" in self.type_ or "Buff" in self.type_):
            self.statMutation(target)
        
            stats = {
                "strength": "Strength",
                "magic": "Magic",
                "defense": "Defense",
                "resistance": "Resistance",
                "luck": "Luck",
                "hit": "Hit",
                "speed": "Speed"
            }
            
            for setS in self.mutate:
                if self.canStack and self.stacks > 0:
                    number = setS[1] - self.stacks if setS[1] < 0 else setS[1] + self.stacks
                else:
                    number = setS[1]
                
                if number < 0:
                    say(f"{Color['magenta']}{target.name}s {stats.get(setS[0])} Was Reduced By {abs(number)}!{Color['reset']}")
                elif number > 0:
                    say(f"{Color['yellow']}{target.name}s {stats.get(setS[0])} Was Increased By {number}!{Color['reset']}")

        if "Prolonger" in self.type_:
            for status in target.statusList:
                if status == self:
                    continue

                if status.family == self.family and random.randint(1, 100) <= self.chanceToProlong:
                    status.duration -= self.prolong
                    if status.duration < 0:
                        status.duration = 0 
                    say(f"{Color['magenta']}{status.name} Had Its Duration Extended By {self.prolong}!{Color['reset']}")
        
        if "Sanity" in self.type_:
            result = None
            if callable(self.sanityCondition):
                result = self.sanityCondition(self, target, damage, enemy)
            
            if result or isinstance(self.sanityCondition, bool) and self.sanityCondition == True:
                if self.sanity > 0:
                    stack = self.stacks if self.canStack else 0
                    target.sanity += self.sanity + stack
                    say(f"{Color['blue']}{target.name} Gained {self.sanity + stack} Sanity!{Color['reset']}")
                elif self.sanity < 0:
                    stack = self.stacks if self.canStack else 0
                    target.sanity -= abs(self.sanity) + stack
                    say(f"{Color['magenta']}{target.name} Lost {abs(self.sanity) + stack} Sanity!{Color['reset']}")

        if "Counter" in self.type_:
            if damage is None or damage <= 0 or self.duration == 0:
                return
    
            if (enemy.lastAction == "Skill" and "Damage" in enemy.lastSkill.type_) or enemy.lastAction == "Attack":
                if enemy.lastAction == "Attack":
                    damageType = "strength"

                elif enemy.lastAction == "Skill":
                    damageType = enemy.lastSkill.statsUsed[0]
                    
                if not self.counterDamage or (self.counterDamage == "physical" and damageType in ["strength", "defense"]) or (self.counterDamage == "magic" and damageType in ["magic", "resistance"]):
                    if self.counterType == "damage":
                        damage = round(damage * self.counter[0] + self.counter[1])
                        setattr(enemy, self.meter, getattr(enemy, self.meter) - damage)
                        say(f"{Color['red']}{enemy.name} Took {damage} From {self.name}!{Color['reset']}")
                    
                    elif self.counterType == "self":
                        damage = round(getattr(target, self.counter[1]) * self.counter[0])
                        setattr(enemy, self.meter, getattr(enemy, self.meter) - damage)
                        say(f"{Color['red']}{enemy.name} Took {damage} From {self.name}!{Color['reset']}")
                    self.remove(target, full=True)

        if "Shift" in self.type_:
            if len(self.shift[0]) == 3 and (self.shift[0][0] in ["fire", "ice", "thunder", "wind", "mighty", "physical"] 
                and 
                isinstance(self.shift[0][1], list) 
                and 
                (isinstance(self.shift[0][2], str) 
                 and 
                 self.shift[0][2] in ["Neutral", "Weak", "Super Weak", "Absorb", "Reflect", "Null", "Resist"])):
                for element, fromAffinities, toAffinity in self.shift:
                    if hasattr(target, element):
                        current = getattr(target, element)
                        if current in fromAffinities:
                            setattr(target, element, toAffinity)
                            say(f"{Color['magenta']}{target.name}s Affinity To {element.capitalize()} Was Changed To {toAffinity}!{Color['reset']}")

            elif len(self.shift[0]) == 2 and (isinstance(self.shift[0], list) 
                  and
                  self.shift[0][0] in ["fire", "ice", "thunder", "wind", "mighty", "physical"] 
                  and
                  self.shift[0][1] in ["Neutral", "Weak", "Super Weak", "Absorb", "Reflect", "Null", "Resist"]):
                for element, toAffinity in self.shift:
                    if hasattr(target, element):
                        current = getattr(target, element)
                        setattr(target, element, toAffinity)
                        say(f"{Color['magenta']}{target.name}s Affinity To {element.capitalize()} Was Changed To {toAffinity}!{Color['reset']}")
        
        newDamage = damage
        
        if not damage == preDamage: return damage
        elif heal: return heal 
        else: return None
        
    def special(self, target, damage=0, enemy=None):
        pass
    
    def coexistCheck(self, target):
        if self.noCoexist:
            for status in target.statusList:
                if status.name in self.noCoexist:
                    status.remove(target, full=True)

    def damageInterupt(self, target, enemy, damage, who):
        return damage

    def speedInterupt(self, target, speed):
        return speed

##------------===------------##

class Skill:
    def __init__(self, name, type_, cost, cooldown, text, hit=0, critical=0, element=None, status=[], stacks=1, count=1, statusTarget="target", willStatus=False, statsUsed=None, recoil=None, customEffect=None, conditional=None, meterDamage="health", damHeal=None, meter=None, healCondition=None, onlyStatusCondition=False, sanLean="Positive", weight=0):
        self.name = name
        self.text = text
        self.cost = cost
        self.hit = hit # Added To Players Hit When Dealing With Damaging Skills
        self.critical = critical # A Higher critical Will Crit More
        self.onCooldown = False
        self.cooldownProgress = 0 # Reaches cooldown, Reset To 0 And Skill Is Usable
        self.usable = True
        self.cooldown = cooldown #
        self.element = element # Fire, Ice, Thunder, Wind, Mighty, Physical | Affects Damage Taken By Enemy
        self.status = status 
        self.stacks = stacks # For Skills That Inflict Statuses With stacking
        self.count = count
        self.statusTarget = statusTarget # For Healing Skills That Inflict Statuses
        self.willStatus = willStatus # Gurrante Status
        self.onlyStatusCondition = onlyStatusCondition # For Condtional Statuses
        self.type_ = type_ # Damage (MultiHit), Healing, Status, Passive | Tuple | Can Be Multiple, Expect For Passive
        self.statsUsed = statsUsed # For Damage And Healing
        # (Damaging Stat, Defensive Stat, Multiplier) Damage Tuple | ([[Used Stat One, Percent One], [Used Stat One, Percent One]], Meter(Health or Mana)) Healing Tuple
        self.recoil = recoil # [True, Percent]
        self.customEffect = customEffect
        self.conditional = conditional
        self.meterDamage = meterDamage # Meter to damage | health/mana
        self.damHeal = damHeal
        self.meter = meter # Used for damHeal
        self.healCondition = healCondition
        self.sanLean = sanLean
        self.weight = weight

    def turnCooldown(self):
        if self.onCooldown == True:
            self.cooldownProgress += 1

            if self.cooldownProgress >= self.cooldown:
                self.cooldownProgress = 0
                self.onCooldown = False
                self.usable = True
            
            else:
                self.usable = False

    # Core Pieces
    def useCheck(self, user, target, who="player"):
        if self.usable == True or who != "player":
            say(f"{user.name} Used {self.name}!")

            if who == "player":
                self.onCooldown = True
                self.usable = False

            if (self.hit + (user.hit * 0.5)) >= random.randint(1, 100) + round(target.luck * 0.25):
                return True
            else:
                say(f"It Missed!")
                user.sanity -= 1
                user.lastAction = "Miss"
                if who == "player": self.cooldownProgress += 1
                return False
    
    def applyStatus(self, user, target, how="damage"):
        if how == "damage":
            # Runs Only If Skill Has A Status
            if self.status:
                for status in self.status:
                    if not isinstance(status, list):
                        if random.randint(1, 100) + user.luck >= target.luck + 35 or self.willStatus == True:
                            if self.statusTarget == "user":
                                status.inflict(user, self.stacks, self.count)
                            elif self.statusTarget == "target":
                                status.inflict(target, self.stacks, self.count)
                            if self.sanLean == "Positive":
                                user.sanity += 1
                            elif self.sanLean == "Negative":
                                user.sanity -= 1
                    else:
                        if not isinstance(status[1], str) and any(s.name == check.name for s in target.statusList for check in status[1:]):
                            if self.statusTarget == "user":
                                status[0].inflict(user, self.stacks, self.count)
                            elif self.statusTarget == "target":
                                status[0].inflict(target, self.stacks, self.count)
                            if self.sanLean == "Positive":
                                user.sanity += 1
                            elif self.sanLean == "Negative":
                                user.sanity -= 1
                        
                        elif isinstance(status[1], str) and any(s.family == status[1] for s in target.statusList):
                            if self.statusTarget == "user":
                                status[0].inflict(user, self.stacks, self.count)
                            elif self.statusTarget == "target":
                                status[0].inflict(target, self.stacks, self.count)
                            if self.sanLean == "Positive":
                                user.sanity += 1
                            elif self.sanLean == "Negative":
                                user.sanity -= 1
                        
                        else:
                            if (random.randint(1, 100) + user.luck >= target.luck + 35  or self.willStatus == True) and not self.onlyStatusCondition:
                                if self.statusTarget == "user":
                                    status[0].inflict(user, self.stacks, self.count)
                                elif self.statusTarget == "target":
                                    status[0].inflict(target, self.stacks, self.count)
                            if self.sanLean == "Positive":
                                user.sanity += 1
                            elif self.sanLean == "Negative":
                                user.sanity -= 1
        
        elif how == "heal":
            # Runs Only If Skill Has Statuses
            if self.status:
                for status in self.status:
                    if self.statusTarget == "user":
                        status.inflict(user, self.stacks, self.count)
                    elif self.statusTarget == "target":
                        status.inflict(target, self.stacks, self.count)
                    user.sanity += 1

    # Damage Pieces
    def bonusChecks(self, user, target, actions, damage):
        strikes = []
        
        # Critical
        if (user.luck + self.critical) >= random.randint(1, 300):
            damage *= 2
            say(f"{Color['yellow']}Critical Strike!{Color['reset']}")
            if self.sanLean == "Positive":
                user.sanity += 2
            elif self.sanLean == "Negative":
                user.sanity -= 1
            strikes.append("Critical")

        # Precision
        totalHit = self.hit + (user.hit * 0.5)
        if totalHit > 100:
            say(f"{Color['red']}Precision Strike!{Color['reset']}")
            overflow = max(0, totalHit - 50) 
            damage = round(damage * ((overflow * 0.20) / 10))
            if self.sanLean == "Positive":
                user.sanity += 2
            elif self.sanLean == "Negative":
                user.sanity -= 1
            strikes.append("Precision")
        
        if totalHit >= 200:
            say(f"{Color['yellow']}Super {Color['red']}Precision Strike!{Color['reset']}")
            overflow = max(0, totalHit - 175)
            damage = round(damage * ((overflow  * 0.40) / 10))
            if self.sanLean == "Positive":
                user.sanity += 3
            elif self.sanLean == "Negative":
                user.sanity -= 2
            strikes.append("Super Precision")
        
        # Conditonals
        if self.conditional:
            damage = self.conditional(self, damage, user, target, actions, strikes)

        # Status Infliction
        self.applyStatus(user, target)
            
        return damage
            
    def calculateDamage(self, user, target, who="player", actions=1):
        reflect = False
        absorb = False
        if who == "player":
            # Element Check And Damage Calculation | Player Only
            damage = 0
            if self.element:
                if getattr(target, self.element) == "Weak":
                    damage = round(max(0, getattr(user, self.statsUsed[0]) + random.randint(1, 5) - (getattr(target, self.statsUsed[1]) // 2)) * self.statsUsed[2])
                    damage = round(damage * 1.5)
                    say(f"{Color['red']}Effective Strike!{Color['reset']}")
                    if self.sanLean == "Positive":
                        user.sanity += 2
                    elif self.sanLean == "Negative":
                        user.sanity -= 1
                    target.sanity -= 2
                    type_ = "Weak"

                elif getattr(target, self.element) == "Super Weak":
                    damage = round(max(0, getattr(user, self.statsUsed[0]) + random.randint(1, 5) - (getattr(target, self.statsUsed[1]) // 2)) * self.statsUsed[2])
                    damage *= 2
                    say(f"{Color['red']}Super Effective Strike!{Color['reset']}")
                    if self.sanLean == "Positive":
                        user.sanity += 3
                    elif self.sanLean == "Negative":
                        user.sanity -= 2
                    target.sanity -= 3
                    type_ = "Super Weak"
                
                elif getattr(target, self.element) == "Neutral":
                    damage = round(max(0,  getattr(user, self.statsUsed[0]) + random.randint(1, 5) - (getattr(target, self.statsUsed[1]) // 2)) * self.statsUsed[2])
                    type_ = "Neutral"
                    
                elif getattr(target, self.element) == "Resist":
                    damage = round(max(0, getattr(user, self.statsUsed[0]) + random.randint(1, 5) - (getattr(target, self.statsUsed[1]) // 2)) * self.statsUsed[2])
                    damage = round(damage * 0.5)
                    say(f"{Color['green']}Resisted Strike!{Color['reset']}")
                    type_ = "Resist"

                elif getattr(target, self.element) == "Null":
                    damage = 0
                    say(f"Strike Nulled!")
                    type_ = "Null"
                    user.lastAction = "Whiff"
                
                elif getattr(target, self.element) == "Reflect":
                    damage = round(max(0, getattr(user, self.statsUsed[0]) + random.randint(1, 5) - (getattr(target, self.statsUsed[1]) // 2)) * self.statsUsed[2])
                    damage = round(damage * 0.5)
                    reflect = True
                    say(f"{Color['yellow']}Strike Reflected!{Color['reset']}") 
                    user.sanity -= 3
                    type_ = "Reflect"
                    user.lastAction = "Whiff"

                elif getattr(target, self.element) == "Absorb":
                    damage = round(max(0, getattr(user, self.statsUsed[0]) + random.randint(1, 5) - (getattr(target, self.statsUsed[1]) // 2)) * self.statsUsed[2])
                    damage = round(damage * 0.5)
                    absorb = True
                    say(f"{Color['blue']}Strike Absorbed!{Color['reset']}") 
                    user.sanity -= 2
                    type_ = "Absorb"
                    user.lastAction = "Whiff"
            
            else:
                damage = round(max(0,  getattr(user, self.statsUsed[0]) + random.randint(1, 5) - (getattr(target, self.statsUsed[1]) // 2)) * self.statsUsed[2])
                type_ = "Neutral"
                
        else: # Enemy Only
            damage = round(max(0,  getattr(user, self.statsUsed[0]) + random.randint(1, 5) - (getattr(target, self.statsUsed[1]) // 2 if self.statsUsed[1] is not None else 0)) * self.statsUsed[2])
        
        if who == "player":
            if type_ in ["Weak", "Super Weak", "Neutral", "Resist"]:
                damage = self.bonusChecks(user, target, actions, damage)
        else:
            damage = self.bonusChecks(user, target, actions, damage)
    
        return damage, reflect, absorb

    def damageHeal(self, user, damage):
        heal = round(damage * self.damHeal)

        current = getattr(user, self.meter)
        cap = getattr(user, f"max{self.meter.capitalize()}")

        restored = min(heal, cap - current)
        setattr(user, self.meter, current + restored)
        say(f"{Color['green']}{user.name}s {self.meter.capitalize()} Was Restored By {heal}!{Color['reset']}")

    def applyDamage(self, user, target, damage, reflect=False, absorb=False):
        for status in user.statusList[:]: 
            if callable(status.damageInterupt):
                damage = status.damageInterupt(user, target, damage, "user")

        for status in target.statusList[:]: 
            if callable(status.damageInterupt):
                damage = status.damageInterupt(target, user, damage, "target")
                
        multiHit = False
        raDamage = damage
        
        # Health Shield Check
        shield = False if not any(s.name == "Health Shield" for s in target.statusList) else True
        
        # Multi Hit Check
        for type_ in self.type_:
            if isinstance(type_, list):
                if type_[0] == "MultiHit":
                    multiAmount = type_[1]() if callable(type_[1]) else type_[1]
                    multiHit = True

        recoil = 0
        
        if multiHit == True:    
            returnDamage = 0
            hits = 0

            if not target.wasHit:
                user.attackHits = 0

            for i in range(0, multiAmount):
                if user.hit + random.randint(1, 20) >= random.randint(1, 110) or returnDamage == 0:
                    if not reflect and not absorb and not shield:
                        say(f"{Color['red']}{user.name} Dealt {damage} To {target.name}!{Color['reset']}")
                        target.health -= damage

                    else:
                        raDamage += damage
                    user.attackHits += 1
                    hits += 1
                    recoil += damage
                    returnDamage += damage
                    damage -= round(damage * 0.30) # Each Hit Deals 30% Less Damage
                else:
                    say(f"It Missed!")
            damage = returnDamage
        else:
            if not target.wasHit:
                user.attackHits = 1
            else: user.attackHits += 1
            if not reflect and not absorb and not shield:
                say(f"{Color['red']}{user.name} Dealt {damage} To {target.name}s {self.meterDamage.capitalize()}!{Color['reset']}")
                setattr(target, self.meterDamage, getattr(target, self.meterDamage) - damage)
            recoil += damage
            hits = 1
        
        # Absorb/Reflect
        if reflect:
            say(f"{Color['red']}{user.name} Took {raDamage}!{Color['reset']}")
            user.health -= raDamage
            user.sanity -= 6
            user.attackHits = 0
        
        elif absorb:
            say(f"{Color['green']}{target.name}s Health Was Healed By {raDamage}!{Color['reset']}")
            target.health += raDamage
            user.sanity -= 5
            user.attackHits = 0
        
        elif shield:
            say(f"{Color['cyan']}{target.name}s Health Shield Blocked The Damage! Health Shield Lost {user.attackHits} Stacks!{Color['reset']}")
            next(s for s in target.statusList if s.name == "Health Shield").stacks -= hits
            user.attackHits = 0

        else: target.wasHit = True

        # Recoil Damage | Only If Skill Has Recoil
        if self.recoil and self.recoil[0]:
            recoil = round(recoil * (self.recoil[1] / 100))
            say(f"{Color['magenta']}{user.name} Took {recoil} From Their Attack!{Color['reset']}")
            user.health -= recoil
            if user.health < 0:
                user.health = 0
            user.sanity -= 2

        if shield:
            damage = 0 # For counters and other statuses/passives that want damage, set to 0 as to not trigger
        
        if self.damHeal:
            if self.healCondition is None or self.healCondition(damage, user, target):
                self.damageHeal(user, damage)
        
        if isinstance(user, Enemy) and isinstance(self, EnemySkill) and self.deathBlock and target.health <= 0:
            say(f"{Color['yellow']}{target.name} Holds On At {self.deathBlock} Health!{Color['reset']}")
            target.health = self.deathBlock
        
        if isinstance(self, EnemySkill):
            if self.followUp:
                if self.followUp[1](user, target):
                    ogStrength, ogMagic = user.strength, user.magic
                    user.strength, user.magic = ogStrength // 2, ogMagic // 2
                    self.followUp[0].effect(user, target, 0)
                    user.strength, user.magic = ogStrength, ogMagic
        
        return damage
    
    def damageEffect(self, user, target, who="player", actions=1):
        if self.useCheck(user, target, who):
            damage, reflect, absorb = self.calculateDamage(user, target, who, actions)
            return self.applyDamage(user, target, damage, reflect, absorb)
        return None

    # Healing Pieces
    def calculateHeal(self, user, target):
        heal = 0
        for setS in self.statsUsed[0]:
            heal += round((setS[1] * getattr(user, setS[0])) / 100)
            if len(setS) == 3:
                heal = round(heal * setS[2]())

        if self.conditional:
            heal = self.conditional(self, heal, user, target)

        return heal
    
    def applyHeal(self, user, heal, who="player"):
        # Critical
        if (user.luck + self.critical) >= random.randint(1, 350):
            heal *= 2
            user.sanity += 2
            say(f"{Color['yellow']}Critical Heal!{Color['reset']}")

        say(f"{Color['green']}{user.name}s {self.statsUsed[1].capitalize()} Was Restored By {heal}!{Color['reset']}")
        if self.statsUsed[1] == "health":
            user.health += heal
            user.health = min(user.health, user.maxHealth)
        elif self.statsUsed[1] == "mana" and who == "player":
            user.mana += heal
            user.mana = min(user.mana, user.maxMana)
        user.sanity += 1
        return heal

    def healEffect(self, user, target, who="player"):
        if self.usable == True or who != "player":
            say(f"{user.name} Used {self.name}!")

            if who == "player":
                self.onCooldown = True
                self.usable = False
        self.applyStatus(user, target, how="heal")
        heal = self.calculateHeal(user, target)
        self.applyHeal(user, heal, who)
        return heal

    # Other Pieces
    def Status(self, user, who, target, actions=1):
        say(f"{user.name} Used {self.name}!")
        if self.usable == True or who != "player":

            if who == "player":
                self.onCooldown = True
                self.usable = False

        if self.conditional:
            self.conditional(self, user, target, actions)

        statuses = self.status[:]
        random.shuffle(statuses)

        for status in statuses:
            if isinstance(status, list):
                continue
            
            if self.statusTarget == "user":
                status.inflict(user, self.stacks)
                
            else:
                status.inflict(target, self.stacks)
                
            if status.family != "Mental":
                user.sanity += 1
        return None

    # Other
    def passive(self, user, target, damage):
        pass
    
    def toDict(self):
        return {"name": self.name}

    def fromDict(data):
        skill = copy.copy(PlayerSkill.allSkills[data["name"]])
        skill.onCooldown = False
        skill.cooldownProgress = 0
        skill.usable = True
        return skill

class PlayerSkill(Skill):
    allSkills = {}
    allScrolls = {}

    def __init__(self, name, type_, cost, cooldown, text, hit=0, critical=0, element=None, status=[], stacks=1, count=1, statusTarget="target", willStatus=False, statsUsed=None, recoil=None, customEffect=None, conditional=None, meterDamage="health", damHeal=None, meter=None, healCondition=None, onlyStatusCondition=False, sanLean="Positive", weight=0):
        super().__init__(name, type_, cost, cooldown, text, hit, critical, element, status, stacks, count, statusTarget, willStatus, statsUsed, recoil, customEffect, conditional, meterDamage, damHeal, meter, healCondition, onlyStatusCondition, sanLean, weight)
        PlayerSkill.allSkills[self.name] = self
        
        cost = 25

        cost += round(10 * (self.cost // 2))
        cost += round(8 * self.cooldown)

        # Search For Statuses
        if status: cost += sum(5 for s in status)
        if stacks > 1: cost += 5 * stacks
        if willStatus: cost += 10 * len(status)
        
        # Damage Skills
        if "Damage" in type_: cost += round(5 * self.statsUsed[2])
        if len(self.type_) >= 2 and isinstance(type_, list) and "MultiHit" in self.type_[1]:
            cost += 5 * (type_[1][1] if not callable(type_[1][1]) else 2) 
        if critical >= 80: cost += critical // 1.5
        if hit >= 80: cost += hit 
        if recoil: cost -= 20
        
        # Other
        if damHeal: cost += 20
        if conditional: cost += 15
        if customEffect: cost += 20
        if self.statsUsed:
            if "Healing" in type_: 
                max_ = max([group[1] for list_ in self.statsUsed if isinstance(list_, list) for group in list_ if isinstance(group, tuple)])
                cost += (2 * max_)
        if "Status" in type_: cost += 15
        if "Special" in type_: cost += 20
        if "Passive" in type_: cost *= 20
        cost = int(cost)
            
        PlayerSkill.allScrolls[self.name] = Item(f"Scroll [{self.name}]", f"Learn the skills {self.name}.", ["Skill"], 1, skill=self, coinCost=cost, gpCost=cost * 10, useType="Overworld")

    def effect(self, user, target, actions=1):
        user.lastSkill = self
        user.lastAction = "Skill"
        if self.customEffect:
            return self.customEffect(self, user, target, actions)
        
        if "Damage" in self.type_:
            return self.damageEffect(user, target, "player", actions)
        
        if "Healing" in self.type_:
            return self.healEffect(user, target, "player")
        
        if "Status" in self.type_:
            return self.Status(user, "player", target, actions)

class EnemySkill(Skill):
    allSkills = {}

    def __init__(self, name, type_, text, weight=1, condition=False, opener=False, finsher=False, weightConditional=None, hit=0, critical=0, element=None, status=[], stacks=1, count=1, statusTarget="target", willStatus=False, statsUsed=None, recoil=None, customEffect=None, conditional=None, meterDamage="health", damHeal=None, meter=None, healCondition=None, onlyStatusCondition=False, deathBlock=False, useType="Normal", sanLean="Positive", followUp=None):
        super().__init__(name, type_, 0, 0, text, hit, critical, element, status, stacks, count, statusTarget, willStatus, statsUsed, recoil, customEffect, conditional, meterDamage, damHeal, meter, healCondition, onlyStatusCondition, sanLean)
        self.weight = weight
        self.condition = condition
        self.opener = opener
        self.finisher = finsher
        self.useType = useType
        self.deathBlock = deathBlock
        self.weightConditional = weightConditional
        self.followUp = followUp
        EnemySkill.allSkills[self.name] = self
    
    def effect(self, user, target, actions=1):
        user.lastSkill = self
        if user.lastAction != "Ultimate":
            user.lastAction = "Skill"

        if self.customEffect:
            return self.customEffect(self, user, target, actions)
        
        if "Damage" in self.type_:
            return self.damageEffect(user, target, "enemy", actions)
        
        if "Healing" in self.type_:
            return self.healEffect(user, target, "enemy")
        
        if "Status" in self.type_:
            return self.Status(user, "enemy", target, actions)

class BuddySkill:
    def __init__(self, name, type_, text, hit=0, critical=0, status=[], stacks=1, count=1, statusTarget="target", willStatus=False, statsUsed=None, customEffect=None, conditional=None, onlyStatusCondition=False):
        self.name = name
        self.type_ = type_
        self.text = text
        self.hit = hit
        self.critical = critical
        self.status = status
        self.stacks = stacks
        self.count = count
        self.statusTarget = statusTarget
        self.willStatus = willStatus
        self.statsUsed = statsUsed
        self.customEffect = customEffect
        self.conditional = conditional
        
    # Core Pieces
    def useCheck(self, buddy, enemy):
        if self.hit + buddy.talent >= random.randint(1, 55) + round(enemy.luck * 0.30):
            say(f"{buddy.name} Used {self.name}!")
            return True
        else:
            say(f"It Missed!")
            return False
    
    def applyStatus(self, buddy, player, enemy):
        if "Damage" in self.type_:
            for status in self.status:
                if random.randint(1, 50) + buddy.talent >= round(enemy.luck * 0.25) + 35 or self.willStatus == True:
                    if self.statusTarget == "user":
                        status.inflict(player, self.stacks, self.count)
                        
                    elif self.statusTarget == "target":
                        status.inflict(enemy, self.stacks, self.count)
        else:
            for status in self.status:
                status.inflict(player, self.stacks, self.count)
                                        
    # Damage Pieces
    def bonusChecks(self, damage, buddy, player, enemy, result, actions=1):
        # Critical
        if (buddy.talent + self.critical) >= random.randint(1, 200):
            damage = round(damage * 1.5)
            say(f"{Color['yellow']}Critical Strike!{Color['reset']}")

            if (buddy.talent + self.critical) >= random.randint(1, 400):
                damage = round(damage * 2)
                say(f"{Color['yellow']}Super Critical Strike!{Color['reset']}")

        # Conditonals
        if self.conditional:
            damage = self.conditional(self, damage, buddy, player, enemy, result, actions=1)

        # Status Infliction
        self.applyStatus(buddy, player, enemy)
        
        return damage
    
    def calculateDamage(self, buddy, player, enemy, result, actions=1):
        budStat = getattr(buddy, self.statsUsed[0])
        eneStat = getattr(enemy, self.statsUsed[1])
        multiplier = self.statsUsed[2]
        roll = random.randint(1, 3)

        attackPower = budStat * roll
        defensePower = (eneStat // 6) * 5

        damage = max(0, round((attackPower - defensePower) * multiplier))

        if damage > 0:
            damage = self.bonusChecks(damage, buddy, player, enemy, result, actions)
        
        return damage
    
    def applyDamage(self, buddy, player, enemy, damage, ignore=False):
        if not ignore:
            for status in enemy.statusList: 
                if callable(status.damageInterupt):
                    damage = status.damageInterupt(enemy, player, damage, "target")
                
        multiHit = False        
        # Health Shield Check
        shield = False if not any(s.name == "Health Shield" for s in enemy.statusList) else True
        
        # Multi Hit Check
        for type_ in self.type_:
            if isinstance(type_, list):
                if type_[0] == "MultiHit":
                    multiAmount = type_[1]() if callable(type_[1]) else type_[1]
                    multiHit = True
        
        if multiHit == True:    
            for i in range(0, multiAmount):
                if buddy.talent + random.randint(1, 25) >= random.randint(1, 70):
                    if not shield:
                        say(f"{Color['red']}{buddy.name} Dealt {damage} To {enemy.name}!{Color['reset']}")
                        enemy.health -= damage

                    damage -= round(damage * 0.25) # Each Hit Deals 25% Less Damage
                else:
                    say(f"It Missed!")
        
        else:
            if not shield:
                say(f"{Color['red']}{buddy.name} Dealt {damage} To {enemy.name}s Health!{Color['reset']}")
                enemy.health -= damage

        if shield:
            say(f"{Color['cyan']}{enemy.name}s Health Shield Blocked All {buddy.name}s Damage!{Color['reset']}")
    
    def damageEffect(self, buddy, player, enemy, result, actions=1):
        if self.useCheck(buddy, enemy):
            damage = self.calculateDamage(buddy, player, enemy, result, actions)
            self.applyDamage(buddy, player, enemy, damage)
    
    # Healing Pieces
    def calculateHeal(self, buddy, player, enemy, result, actions=1):
        heal = 0
        for setS in self.statsUsed[0]:
            if setS[0] in ["attack", "talent"]:
                heal += round((setS[1] * getattr(buddy, setS[0])) / 10)
            else:
                heal += round((setS[1] * getattr(player, setS[0])) / 100)
            if len(setS) == 3:
                heal = round(heal * setS[2]())

        if self.conditional:
            heal = self.conditional(self, heal, buddy, player, enemy, result, actions)

        return heal
    
    def applyHeal(self, heal, buddy, player):
        # Critical
        if (buddy.talent + random.randint(1, 50)) >= random.randint(1, 200):
            heal *= 2
            say(f"{Color['yellow']}Critical Heal!{Color['reset']}")

        say(f"{Color['green']}{player.name}s {self.statsUsed[1].capitalize()} Was Restored By {heal}!{Color['reset']}")
        if self.statsUsed[1] == "health":
            player.health += heal
            player.health = min(player.health, player.maxHealth)
        elif self.statsUsed[1] == "mana":
            player.mana += heal
            player.mana = min(player.mana, player.maxMana)

    def healEffect(self, buddy, player, enemy, result, actions=1):
        say(f"{buddy.name} Used {self.name}!")
        self.applyStatus(buddy, player, enemy)
        heal = self.calculateHeal(buddy, player, enemy, result, actions)
        self.applyHeal(heal, buddy, player)
    
    # Other
    def Status(self, buddy, player, enemy, result, actions=1):
        say(f"{buddy.name} Used {self.name}!")

        if self.conditional:
            self.conditional(self, buddy, player, enemy, result, actions)

        statuses = self.status[:]
        random.shuffle(statuses)

        for status in statuses:
            if isinstance(status, list):
                continue
            
            if self.statusTarget == "user":
                status.inflict(player, self.stacks)
                
            else:
                status.inflict(enemy, self.stacks)
    
    def passive(self, buddy, player, enemy, result, actions=1):
        pass
    
    # Actual
    def effect(self, buddy, player, enemy, result, actions=1):
        if self.customEffect:
            return self.customEffect(self, buddy, player, enemy, result, actions)
        
        if "Damage" in self.type_:
            return self.damageEffect(buddy, player, enemy, result, actions)
        
        if "Healing" in self.type_:
            return self.healEffect(buddy, player, enemy, result, actions)
        
        if "Status" in self.type_:
            return self.Status(buddy, player, enemy, result, actions)
        
##------------===------------##

class Sigil: 
    allSigils = {}

    def __init__(self, name, flavor, effect, affinity, trigger, statChange, coinCost=0, gpCost=0, battleEffect=None):
        self.name = name
        self.flavor = flavor
        self.effect = effect
        self.affinity = affinity   # Power/Survival/Utility
        self.coinCost = coinCost
        self.gpCost = gpCost
        self.trigger = trigger # afterAction/battleStart/afterEnemy/statusTick/statusTickEnemy
        self.statChange = statChange # dict e.g. {("strength", 5), ("magic", -10)}
        self.battleEffect = battleEffect # None or a function for in-battle effects
        Sigil.allSigils[self.name] = self
   
    def equipSigil(self, player):
        if len(player.sigils) >= 3:
            print("No open sigil slots!")
            return
        
        player.sigils.append(self)
        player.reserveSigils.remove(self)
        for stat, amount in self.statChange:
            setattr(player, stat, getattr(player, stat) + amount)

        for stat in ["strength", "magic", "defense", "resistance", "luck", "hit", "speed", "maxHealth", "maxMana"]:
            if stat not in ["speed", "maxHealth", "maxMana"]:
                setattr(player, stat, max(1, getattr(player, stat)))
            
            elif stat == "speed":
                setattr(player, stat, max(5, getattr(player, stat)))
            
            elif stat in ["maxHealth", "maxMana"]:
                setattr(player, stat, max(50, getattr(player, stat)))
                if getattr(player, stat[3:].lower()) > getattr(player, stat):
                    setattr(player, stat[3:].lower(), getattr(player, stat))

    def unequipSigil(self, player):
        player.sigils.remove(self)
        player.reserveSigils.append(self)
        
        # Reset to sigilless values then reapply remaining sigils
        for stat in ["maxHealth", "maxMana", "strength", "magic", "defense", "resistance", "luck", "hit", "speed"]:
            if stat == "maxHealth":
                setattr(player, stat, getattr(player, f"sigillessMaxHealth"))
                continue
        
            if stat == "maxMana":
                setattr(player, stat, getattr(player, f"sigillessMaxMana"))
                continue
                        
            setattr(player, stat, getattr(player, f"sigilless{stat.capitalize()}"))
        
        for equipped in player.sigils:
            for stat, amount in equipped.statChange:
                setattr(player, stat, getattr(player, stat) + amount)

        for stat in ["maxHealth", "maxMana", "strength", "magic", "defense", "resistance", "luck", "hit", "speed"]:
            if stat not in ["speed", "maxHealth", "maxMana"]:
                setattr(player, stat, max(1, getattr(player, stat)))
                
            elif stat == "speed":
                setattr(player, stat, max(5, getattr(player, stat)))
                
            elif stat in ["maxHealth", "maxMana"]:
                setattr(player, stat, max(50, getattr(player, stat)))
                if getattr(player, stat[3:].lower()) > getattr(player, stat):
                    setattr(player, stat[3:].lower(), getattr(player, stat))

    def toDict(self):
        return {
            "name": self.name,
        }

    def fromDict(data):
        sigil = copy.copy(Sigil.allSigils[data["name"]])
        return sigil

class Buddy:
    allBuddies = {}
    
    def __init__(self, name, affinity, attack, talent, speed, passive, skill, gpCost):
        self.name = name
        self.affinity = affinity # Power/Support/Utility
        self.attack = attack # The equivilant of Strength/Magic
        self.talent = talent # The equivilant of Hit/Luck
        self.speed = speed # The equivilant of Speed
        self.buddyMeter = 0
        self.passive = passive
        self.skill = skill
        self.gpCost = gpCost
        self.level = 0
        self.levelGoal = 100
        self.levelValue = 0
        self.treats = {}
        Buddy.allBuddies[self.name] = self
    
    def levelUp(self, sim=False):
        self.level += 1
        self.levelValue -= self.levelGoal
        self.levelGoal += 200

        if not sim:
            print(f"{Color['cyan']}{self.name} Leveled Up!{Color['reset']}")
            line("chrMain")
        
        for stat in ["attack", "talent"]:
            oldValue = getattr(self, stat)
            newValue = getattr(self, stat) + (3 if stat == "attack" else 2)
            setattr(self, stat, newValue)
            if not sim:
                print(f"{stat.capitalize()}: {Color['cyan']}{oldValue}{Color['reset']} -> {Color['cyan']}{newValue}{Color['reset']}")
        if not sim:
            line("chrMain")
        
        if not sim:
            input("?>")
        
    def toDict(self):
        return {
            "name": self.name,
            "level": self.level,
            "levelValue": self.levelValue,
            "levelGoal": self.levelGoal,
            "attack": self.attack,
            "talent": self.talent,
            "speed": self.speed,
            "treats": self.treats
        }

    def fromDict(data):
        buddy = copy.copy(Buddy.allBuddies[data["name"]])
        buddy.level = data["level"] if "level" in data.keys() else 1
        buddy.levelValue = data["levelValue"] if "levelValue" in data.keys() else 0
        buddy.levelGoal = data["levelGoal"] if "levelGoal" in data.keys() else 100
        buddy.attack = data["attack"] if "attack" in data.keys() else Buddy.allBuddies[data["name"]].attack
        buddy.talent = data["talent"] if "talent" in data.keys() else Buddy.allBuddies[data["name"]].talent
        buddy.speed = data["speed"] if "speed" in data.keys() else Buddy.allBuddies[data["name"]].speed
        buddy.treats = data["treats"] if "treats" in data.keys() else {}
        return buddy
    
class Item:
    allItems = {}
    
    def __init__(self, name, effect, type_, maxAmount=0, heal=None, status=None, removeAmount=None, removeChance=False, removeTarget="Negative", damage=None, hit=0, element=None, stacks=1, count=1, skill=None, target="enemy", useType="Free", coinCost=1, gpCost=1, extraEffect=None):
        self.name = name
        self.playerAmount = 0
        self.maxAmount = maxAmount
        self.effect = effect
        self.type_ = type_ #Damage/StatusI/StatusC/Heal/Boon
        self.heal = heal # [("health", 30), ("mana", 15)]
        self.status = status # What Status To Inflict
        self.stacks = stacks
        self.count = count
        self.removeAmount = removeAmount
        self.removeChance = removeChance
        self.removeTarget = removeTarget
        self.damage = damage # (10, attackTimes)
        self.hit = hit
        self.element = element # The Element Of The Damage | Needs Damage To Not Be None
        self.skill = skill
        self.target = target
        self.useType = useType
        self.extraEffect = extraEffect
        self.coinCost = coinCost
        self.gpCost = gpCost
        Item.allItems[self.name] = self

    def tracker(self, amount, type_, player):
        existing = next((item for item in player.items if item.name == self.name), None)

        if existing is None:
            item = copy.copy(self)
            item.playerAmount = 0
        else:
            item = existing

        if type_ == "Add":
            item.playerAmount += amount
        elif type_ == "Remove":
            item.playerAmount -= amount

        item.playerAmount = max(0, min(item.playerAmount, item.maxAmount))

        if item.playerAmount > 0 and existing is None:
            player.items.append(item)

        elif item.playerAmount <= 0 and existing is not None:
            player.items.remove(existing)

    def use(self, player, enemy, actions=None):
        player.lastItem = self
        say(f"{player.name} Used {self.name}!")
        self.tracker(1, "Remove", player)
        reflect = False
        absorb = False
        
        result = None

        if self.extraEffect:
            result = self.extraEffect(self, player, enemy)
        
        if "StatusI" in self.type_ and not "Damage" in self.type_:
            anyNew = any(not any(s.name == status.name for s in (enemy.statusList if self.target == "enemy" else player.statusList)) for status in self.status)
            for status in self.status:
                if self.target == "player":
                    status.inflict(player, self.stacks)
                elif self.target == "enemy":
                    status.inflict(enemy, self.stacks)

            if not anyNew and not any(not isinstance(t, list) and t != "StatusI" for t in self.type_):
                say(f"There Was No Effect!")

        if "StatusC" in self.type_:
            cleansed = False
            for status in player.statusList[:]:
                if status.name in self.status:
                    status.remove(player, full=True)
                    status.statMutation(player)
                    say(f"{Color['green']}{player.name} No Longer Has {status.name}!{Color['reset']}")
                    cleansed = True

            if not cleansed:
                say(f"There Was No Effect!")
        
        if "Cleanse" in self.type_:
            amount = 0
            if self.target == "enemy":
                lisT = enemy.statusList[:]
            else:
                lisT = player.statusList[:]
            random.shuffle(lisT)
            for status in lisT[:]:
                if status.align in self.removeTarget or status.family in self.removeTarget:
                    if not self.removeChance or random.randint(1, 100) >= 35:
                        if self.target == "enemy":
                            status.remove(enemy, full=True)
                        else:
                            status.remove(player, full=True)

                        amount += 1
                
                if amount >= self.removeAmount:
                    break
            
            if amount == 0:
                say("Nothing Happened!")
                    
        if "Heal" in self.type_:
            for stat, amount in self.heal:  
                cap = getattr(player, f"max{stat.capitalize()}")
                current = getattr(player, stat)
                if isinstance(amount, int):
                    restored = min(amount, cap - current)
                elif isinstance(amount, float):
                    restored = min(round(cap * amount), cap - current)
                setattr(player, stat, current + restored)
                say(f"{Color['green']}{stat.capitalize()} Restored By {restored}!{Color['reset']}")
            return restored
            
        if "Damage" in self.type_:
            if (self.hit + player.hit * 0.50) >= random.randint(1, 50) + round(enemy.luck * 0.25):
                damage = self.damage[0]
                if len(self.damage) >= 3:
                    for setS in self.damage[2]:
                        damage += round(getattr(player, setS[0]) * setS[1])

                if result:
                    damage += result
                
                if getattr(enemy, self.element) == "Super Weak":
                    damage = round(damage * 2)
                    say(f"{Color['red']}Effective Strike!{Color['reset']}")
                
                if getattr(enemy, self.element) == "Weak":
                    damage = round(damage * 1.5)
                    say(f"{Color['red']}Effective Strike!{Color['reset']}")
                
                elif getattr(enemy, self.element) == "Resist":
                    damage = round(damage * 0.5)
                    say(f"{Color['green']}Resisted Strike!{Color['reset']}")
                
                elif getattr(enemy, self.element) == "Reflect":
                    damage = round(damage * 0.5)
                    reflect = True
                    say(f"{Color['yellow']}Strike Reflected!{Color['reset']}") 

                elif getattr(enemy, self.element) == "Absorb":
                    damage = round(damage * 0.5)
                    absorb = True
                    say(f"{Color['blue']}Strike Absorbed!{Color['reset']}") 
                    
                elif getattr(enemy, self.element) == "Null":
                    damage = 0
                    say(f"Strike Nulled!")

                if getattr(enemy, self.element) not in ["Reflect", "Absorb", "Null"]:
                    # Critical
                    if (player.luck) >= random.randint(1, 300):
                        damage *= 2
                        say(f"{Color['yellow']}Critical Strike!{Color['reset']}")
                
                    # Precision
                    totalHit = self.hit + (player.hit * 0.5)
                    if totalHit > 100:
                        say(f"{Color['red']}Precision Strike!{Color['reset']}")
                        overflow = max(0, totalHit - 50) 
                        damage = round(damage * ((overflow * 0.20) / 10))

                    if "StatusI" in self.type_:
                        for status in self.status:
                            if random.randint(1, 75) + player.luck >= enemy.luck + 40:
                                if self.target == "player": status.inflict(player, self.stacks, self.count)
                                elif self.target == "enemy": status.inflict(enemy, self.stacks, self.count)
                
                attackTimes = 0
                totalDamage = 0
                hits = self.damage[1] if not callable(self.damage[1]) else self.damage[1]()
                
                while attackTimes < hits:
                    if not reflect and not absorb:
                        say(f"{Color['red']}{player.name} Dealt {damage} To {enemy.name}!{Color['reset']}")
                        enemy.health -= damage
                    totalDamage += damage
                    damage -= round(damage * 0.30) # Each Hit Deals 30% Less Damage
                    attackTimes += 1
                
                # Absorb/Reflect
                if reflect:
                    say(f"{Color['red']}{player.name} Took {totalDamage}!{Color['reset']}")
                    player.health -= totalDamage
                    player.sanity -= 1
                
                elif absorb:
                    say(f"{Color['green']}{enemy.name}s Health Was Healed By {totalDamage}!{Color['reset']}")
                    enemy.health = min(enemy.maxHealth, enemy.health + totalDamage)
                return totalDamage

            else:
                say("It Missed!")
                player.lastAction = "Miss"
                return 0
    
        if "Skill" in self.type_:
            if any(self.skill.name == s.name for s in player.skills + player.reserveSkills):
                print(f"{Color['red']}{player.name} Already Knows {self.skill.name}!{Color['reset']}")
                return None

            self.tracker(1, "Remove", player)
            print(f"{Color['yellow']}{player.name} Learned {self.skill.name}!{Color['reset']}")
            player.reserveSkills.append(copy.deepcopy(self.skill))
            return None

        if "Special" in self.type_:
            self.special(player, enemy)

    def toDict(self):
        return {"name": self.name, "playerAmount": self.playerAmount}

    def fromDict(data):
        item = copy.copy(Item.allItems[data["name"]])
        item.playerAmount = data.get("playerAmount", 1)
        return item
    
class Map:
    allMaps = {}

    def __init__(self, name, tiles, maxY, maxX, scaling, enemies, travelCords, rewards):
        self.version = 1
        self.name = name
        self.tiles = tiles # A Dictionary For The Tiles That The Player Will Walk On
        self.maxY = maxY
        self.maxX = maxX
        self.scaling = scaling # A Tuple | (Lower Number, Higher Number) | Enemies Will Scale Using These Numbers
        self.enemies = enemies # A List Of Enemies Created From A Class 
        self.travelCords = travelCords # [x, y] Where The Player Will Go After Using Fast Travel
        self.rewards = rewards
        Map.allMaps[self.name] = self
    
    def enemyScale(self, player, battleType=str, timed=False, limit=False, extreme=None, cheater=None, wave=None, theme=None, specialBattle=False):
        # Enemy Level Scaling
        minLevel = self.scaling[0]
        maxLevel = self.scaling[1]
        proxyLevel = player.level

        if proxyLevel < minLevel:
            proxyLevel = minLevel

        elif proxyLevel > maxLevel:
            proxyLevel = maxLevel

        levelRange = maxLevel - minLevel

        if levelRange == 0:
            scaleFactor = 1
        else:
            scaleFactor = 1 + 0.5 * ((proxyLevel - minLevel) / levelRange)

        # Enemy Creation And Modification
        if extreme is None:
            extreme = [False, False]
        if not extreme[0]:
            enemy = copy.deepcopy(random.choice(self.enemies))
        else:
            enemy = copy.deepcopy(random.choice(extreme[1]))

        if cheater:
            skills = copy.deepcopy(list(EnemySkill.allSkills.values()))
            ultimateSkills = []

            for skill in skills[:]:
                if skill.useType != "Ultimate":
                    skills.remove(skill)
                    ultimateSkills.append(skill)

            random.shuffle(skills)
            random.shuffle(ultimateSkills)

            enemy = copy.deepcopy(random.choice(self.enemies))
            amount = random.randint(1, 2)

            for i in range(amount):
                if skills:
                    enemy.skills.append(copy.deepcopy(random.choice(skills)))

            ultimateList = [enemy.ultimateSkill]
            for i in range(amount):
                if ultimateSkills:
                    ultimateList.append(copy.deepcopy(random.choice(ultimateSkills)))

            enemy.ultimateSkill = ultimateList

            affinitys = ["Resist"] * 10 + ["Reflect"] * 6 + ["Absorb"] * 4 + ["Null"] * 2

            for affinity in ["fire", "ice", "thunder", "wind", "mighty", "physical"]:
                if random.randint(1, 100) >= 65:
                    setattr(enemy, affinity, random.choice(affinitys))
            
        if wave:
            if wave[0]:
                if wave[1] % 5 == 0:
                    enemy = copy.deepcopy(random.choice(wave[3]))

                enemy_can_tran = True if enemy.transformTo is not None else False

                if enemy_can_tran:
                    transformation = copy.deepcopy(enemy.transformTo)

                if wave[1] >= 3:
                    for stat in ["maxHealth", "strength", "magic", "defense", "resistance"]:
                        if stat == "maxHealth":
                            setattr(enemy, stat, round(getattr(enemy, stat) * (0.5 + random.randint(1,2))))

                            if enemy_can_tran:
                                setattr(transformation, stat, round(getattr(transformation, stat) * (0.5 + random.randint(1,2))))
                            continue

                        setattr(enemy, stat, round(getattr(enemy, stat) + random.randint(wave[2][0], wave[2][1])))
                        if enemy_can_tran:
                            setattr(transformation, stat, round(getattr(transformation, stat) + random.randint(wave[2][0], wave[2][1])))

                    enemy.health = enemy.maxHealth
                    
                    if enemy_can_tran:
                        transformation.health = transformation.maxHealth
                    
                if wave[1] >= 5:
                    for stat in ["luck", "hit", "speed"]:
                        setattr(enemy, stat, round(getattr(enemy, stat) + 5))

                        if enemy_can_tran:
                            setattr(transformation, stat, round(getattr(transformation, stat) + 5))

                if wave[1] >= 10:
                    for stat in ["luck", "hit", "speed"]:
                        setattr(enemy, stat, round(getattr(enemy, stat) + 10))

                        if enemy_can_tran:
                            setattr(transformation, stat, round(getattr(transformation, stat) + 10))

                if enemy_can_tran:
                    enemy.transformTo = transformation

        if theme:
            if theme[1] >= 5 and theme[3] == 1:
                enemy = copy.deepcopy(Enemy.allEnemies[theme[2]])
                                
            elif theme[1] >= 5 and theme[3] == 2:
                enemy = copy.deepcopy(Enemy.allEnemies[theme[2] + " X"])
            
            elif theme[1] >= 5 and theme[3] == 3:
                enemy = copy.deepcopy(Enemy.allEnemies[theme[2] + " EX"])

        for stat in ["maxHealth", "strength", "magic", "defense", "resistance", "luck", "hit", "speed"]:
            setattr(enemy, stat, round(getattr(enemy, stat) * scaleFactor))
        enemy.health = enemy.maxHealth

        for stat in ["strength", "magic", "defense", "resistance", "luck", "hit", "speed"]:
            setattr(enemy, f"base{stat.capitalize()}", getattr(enemy, stat))

        enemy.coin = round(enemy.coin * scaleFactor)
        enemy.exp = round(enemy.exp * scaleFactor)
        
        clear()
        line("battle")
        print(f"{Color['red']}{enemy.name} Encountered!{Color['reset']}")
        line("battle")

        input("?>")

        result = battleLoopFunc(enemy, player, battleType, timed, limit, theme, specialBattle, wave if wave else None)
        return result

    def enemyEncounter(self, player, timed=False, limit=False, logs=True):
        currentTile = self.tiles.get((player.y, player.x))

        if currentTile["type"] in ["hazard", "gateHaz"]:
            if random.randint(1, 100) <= 25:  # 25% encounter chance per step
                if currentTile["hazard"] == "wave":
                    x = random.randint(2,3)
                    for i in range(1, x + 1):
                        line("battle")
                        print(f"{Color['red']}Battle {i}/{x}!{Color['reset']}")
                        line("battle")
                        input("?>")
                        result = self.enemyScale(player, "Wave Map/Main")
                        
                        if result in ["Loss", "Escape"]:
                            break
                    return result 
                else:
                    result = self.enemyScale(player, "Map/Main")
                    return result
        
    def bossEncounter(self, player, boss):
        for s in [["strength", "defense", 2, 3], ["magic", "resistance", 2, 3]]:
            gap = getattr(player, s[0]) - getattr(boss, s[1])
            if gap > 0:
                for i in range(0, gap, s[3]):
                    setattr(boss, f"base{s[1].capitalize()}", getattr(boss,  f"base{s[1].capitalize()}") + s[2])
                    
        greaterE = ([boss.strength, "strength"] if boss.strength >= boss.magic else [boss.magic, "magic"])
        lesserE = (boss.strength if boss.strength < boss.magic else boss.magic)
        greaterP = (player.strength if player.strength >= player.magic else player.magic)
        gap = greaterP - greaterE[0]
        if gap > 0:
            for i in range(0, gap, 4):
                if abs(greaterE[0] - lesserE) <= 5:
                    boss.baseStrength += 2
                    boss.baseMagic += 2
                else:
                    setattr(boss,  f"base{greaterE[1].capitalize()}", getattr(boss,  f"base{greaterE[1].capitalize()}") + 2)
        
        for stat in ["strength", "magic", "defense", "resistance", "luck", "hit", "speed"]:
            setattr(boss, stat, getattr(boss, f"base{stat.capitalize()}"))
        result = battleLoopFunc(boss, player, "Boss Map/Main")
        return result

    def tileBehavior(self, player):
        currentTile = self.tiles.get((player.y, player.x))

        # Hazards
        if currentTile["hazard"] == "poison":
            damage = round(player.maxHealth * 0.03)
            player.health -= damage
            print(f"{Color['red']}{player.name} Took {damage} HP Damage From The Poison!{Color['reset']}")

            if player.health <= 0:
                player.health = 1
        
        elif currentTile["hazard"] == "leech":
            damage = round(player.maxMana * 0.05)
            player.mana -= damage
            print(f"{Color['red']}{player.name} Took {damage} MP Damage From The Soul Leechs!{Color['reset']}")
            
            if player.mana <= 0:
                player.mana = 1
        
        elif currentTile["hazard"] == "healing":
            healthHeal = round(player.maxHealth * 0.50)
            manaHeal = round(player.maxMana * 0.50)
            player.health = min(player.maxHealth, player.health + healthHeal)
            player.mana = min(player.maxMana, player.mana + manaHeal)
            print(f"{Color['green']}{player.name} Healed {healthHeal} HP & {manaHeal} MP!{Color['reset']}")

            if player.health > player.maxHealth:
                player.health = player.maxHealth
            
            if player.mana > player.maxMana:
                player.mana = player.maxMana

        # Types
        if currentTile["type"] == "storage":
            currentTop = 0
            currentBottom = 0

            while True:
                clear()

                print("Item Storage")
                line("items")
                print("")

                # Equipped Items
                topPage = []
                for item in player.items:
                    if not topPage or len(topPage[-1]) == 3:
                        topPage.append([])
                    topPage[-1].append(item)

                if topPage and currentTop >= len(topPage):
                    currentTop = len(topPage) - 1

                print(f"{Color['red']}Current Items | {Color['yellow']}Page: {currentTop + 1}/{len(topPage)}{Color['reset']}")
                line("items")

                if topPage:
                    number = 0

                    for item in topPage[currentTop]:
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
                        if number != len(topPage[currentTop]):
                            print("")
                else:
                    print("No Items!")

                # Stored Items
                bottomPage = []
                for item in player.itemStorage:
                    if not bottomPage or len(bottomPage[-1]) == 5:
                        bottomPage.append([])
                    bottomPage[-1].append(item)

                if bottomPage and currentBottom >= len(bottomPage):
                    currentBottom = len(bottomPage) - 1
                line("items")
                print("")

                print(f"{Color['cyan']}Stored Items | {Color['yellow']}Page: {currentBottom + 1}/{len(bottomPage)}{Color['reset']}")
                line("items")

                if bottomPage:
                    number = 0

                    for item in bottomPage[currentBottom]:
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
                        if number != len(bottomPage[currentBottom]):
                            print("")
                else:
                    print("No Items!")
                line("items")
                print("")

                print(f"S + Item Number (To Store An Item)")
                print(f"E + Item Number (To Take An Item)")
                print("0. Back")

                if currentTop + 1 < len(topPage): print("T1. Next Current Page")
                if currentTop > 0: print("T2. Previous Current Page")

                if currentBottom + 1 < len(bottomPage): print("B1. Next Current Page")
                if currentBottom > 0: print("B2. Previous Current Page")
                
                line("items")

                choice = input("->")

                if choice.startswith("s") or choice.startswith("S"):
                    idx = choice[1:]
                    if topPage and idx.isdigit() and int(idx) < len(topPage[currentTop]):

                        # Check if type is in item storage
                        found = False
                        save = None

                        for item in player.itemStorage:
                            if topPage[currentTop][int(idx)].name == item.name:
                                found = True
                                if topPage[currentTop][int(idx)].playerAmount + item.playerAmount >= item.maxAmount:
                                    save = topPage[currentTop][int(idx)].playerAmount - (item.maxAmount - item.playerAmount)
                                    save = save if save > 0 else None
                                    item.playerAmount += item.maxAmount - item.playerAmount if item.maxAmount - item.playerAmount > 0 else 0
                                    break
                                else:
                                    item.playerAmount += topPage[currentTop][int(idx)].playerAmount
                                    player.items.remove(topPage[currentTop][int(idx)])
                                    break
                        
                        if found:
                            if save:
                                topPage[currentTop][int(idx)].playerAmount = save
                                continue
                            else:
                                continue
                        
                        # Normal
                        else:
                            player.items.remove(topPage[currentTop][int(idx)])
                            player.itemStorage.append(topPage[currentTop][int(idx)])
                        

                if choice.startswith("e") or choice.startswith("E"):
                    idx = choice[1:]
                    if bottomPage and idx.isdigit() and int(idx) < len(bottomPage[currentBottom]):
                        found = False
                        save = None

                        for item in player.items:
                            if bottomPage[currentBottom][int(idx)].name == item.name:
                                found = True
                                if bottomPage[currentBottom][int(idx)].playerAmount + item.playerAmount >= item.maxAmount:
                                    save = bottomPage[currentBottom][int(idx)].playerAmount - (item.maxAmount - item.playerAmount)
                                    save = save if save > 0 else None
                                    item.playerAmount += item.maxAmount - item.playerAmount if item.maxAmount - item.playerAmount > 0 else 0
                                    break

                                else:
                                    item.playerAmount += bottomPage[currentBottom][int(idx)].playerAmount
                                    player.itemStorage.remove(bottomPage[currentBottom][int(idx)])
                                    break
                                    
                        if found:
                            if save:
                                bottomPage[currentBottom][int(idx)].playerAmount = save
                                continue
                            else:
                                continue

                        # Normal
                        else:
                            player.itemStorage.remove(bottomPage[currentBottom][int(idx)])
                            player.items.append(bottomPage[currentBottom][int(idx)])

                if choice.startswith("t") or choice.startswith("T"):
                    idx = choice[1:]

                    if idx.isdigit() and idx == "1":
                        if idx == "1" and currentTop + 1 < len(topPage):
                            currentTop += 1

                    elif idx.isdigit() and idx == "2":
                        if idx == "2" and currentTop > 0:
                            currentTop -= 1

                if choice.startswith("b") or choice.startswith("B"):
                    idx = choice[1:]
                    
                    if idx.isdigit() and idx == "1":
                        if idx == "1" and currentBottom + 1 < len(bottomPage):
                            currentBottom += 1

                    elif idx.isdigit() and idx == "2":
                        if idx == "2" and currentBottom > 0:
                            currentBottom -= 1

                if choice == "0":
                    return "Continue"

        if currentTile["type"] == "shop":
            currentPage = 0

            while True:
                clear()

                print(currentTile["shop"][0])
                line("shop")
                
                page = []
                for item in currentTile["shop"][1]:
                    if isinstance(item, Sigil):
                        if any(item.name == s.name for s in player.sigils + player.reserveSigils):
                            continue
                    if isinstance(item, Skill):
                        if any(PlayerSkill.allScrolls[item.name].skill.name == s.name for s in player.skills + player.reserveSkills) or any(PlayerSkill.allScrolls[item.name].name == i.name for i in player.items):
                            continue 
                    if not page or len(page[-1]) == 5:
                        page.append([])
                    page[-1].append(item)
                if page and currentPage >= len(page):
                    currentPage = len(page) - 1
                
                if page:
                    number = 0
                    for item in page[currentPage][:]:
                        if isinstance(item, Item):
                            current = next((i for i in player.items if i.name == item.name), item)
                            print(f"{number}. {Color['yellow']}{item.name} | {current.playerAmount}/{item.maxAmount} | {item.coinCost}/{item.gpCost}{Color['reset']}")
                            print(f"{Color['green']}{item.effect}{Color['reset']}")
                        elif isinstance(item, Sigil):
                            print(f"{number}. {Color['yellow']}{item.name} | {item.affinity} | {item.coinCost}/{item.gpCost}{Color['reset']}")
                            print(f"{Color['green']}{item.effect}{Color['reset']}")
                        elif isinstance(item, Skill):
                            print(f"{number}. {Color['yellow']}{PlayerSkill.allScrolls[item.name].name} | {PlayerSkill.allScrolls[item.name].playerAmount}/{PlayerSkill.allScrolls[item.name].maxAmount} | {PlayerSkill.allScrolls[item.name].coinCost}/{PlayerSkill.allScrolls[item.name].gpCost}{Color['reset']}")
                            print(f"{Color['green']}{PlayerSkill.allScrolls[item.name].effect}{Color['reset']}")
                            page[currentPage] = [PlayerSkill.allScrolls[item.name] if isinstance(i, Skill) and i.name == PlayerSkill.allScrolls[item.name].skill.name else i for i in page[currentPage]]
                        number += 1
                        line("shop")
                    print("")

                    line("shop")
                    print(f"Coin: {Color['yellow']}{player.coins}{Color['reset']}")
                    print(f"Game Points: {Color['cyan']}{player.gamePoints}{Color['reset']}")
                    print(f"{Color['red']}Type 'Exit' To Leave{Color['reset']}")
                    if currentPage + 1 < len(page): print("Type 'Next' For Next Page")
                    if currentPage > 0: print("Type 'Pre' For Previous Page")
                    line("shop")
                    
                    choice = input("$>")
                    if choice in ["Exit", "exit"]:
                        return "Continue"

                    if choice in ["Next", "next"] and currentPage + 1 < len(page):
                        currentPage += 1

                    if choice in ["Pre", "pre"] and currentPage > 0:
                        currentPage -= 1

                    if choice.isdigit():
                        choice = int(choice)
                        if 0 <= choice <= len(page[currentPage]) - 1:
                            choiceNum = int(choice)
                            print(f"1. {Color['yellow']}Coins{Color['reset']} | 2. {Color['cyan']}GP{Color['reset']} | 3. {Color['red']}Back{Color['reset']}")
                            coins = False
                            points = False
                            purchase = False

                            while True:
                                choice = input("?>")
                                if choice == "1":
                                    coins = True
                                    break
                                elif choice == "2":
                                    points = True
                                    break
                                elif choice == "3":
                                    break
                            
                            if coins or points:
                                while True:
                                    if hasattr(page[currentPage][choiceNum], "maxAmount"):
                                        print(f"How Many?") 
                                        amount = input(f"{page[currentPage][choiceNum].maxAmount}\\")
                                        if amount and amount.isdigit():
                                            amount = int(amount)
                                            if amount != 0:
                                                i = next((s for s in player.items if s.name == page[currentPage][choiceNum].name), page[currentPage][choiceNum]).playerAmount
                                                if not amount + i > page[currentPage][choiceNum].maxAmount:
                                                    if coins:
                                                        price = page[currentPage][choiceNum].coinCost * amount
                                                    elif points:
                                                        price = page[currentPage][choiceNum].gpCost * amount
                                                    else:
                                                        break
                                                else:
                                                    print(f"{Color['red']}Exceeds Max Amount!{Color['reset']}")
                                                    input(">")
                                                    break
                                        else:
                                            break
                                    else: 
                                        if coins:
                                            price = page[currentPage][choiceNum].coinCost
                                        elif points:
                                            price = page[currentPage][choiceNum].gpCost
                                        else:
                                            break
                                    purchase = True
                                    price = int(price)
                                    break

                            if purchase:
                                while True:
                                    quantity = amount if isinstance(page[currentPage][choiceNum], Item) else 1
                                    print(f"{price} For {quantity} {page[currentPage][choiceNum].name}?")
                                    print(f"1. {Color['green']}Yes{Color['reset']} 2. {Color['red']}No{Color['reset']}")

                                    choice = input("?>")

                                    if choice == "1":
                                        if coins and player.coins < price or points and player.gamePoints < price:
                                            print(f"{Color['red']}Not Enough {'Coins' if coins else 'GP'}!{Color['reset']}")
                                            input("?>")
                                            break
                                        if isinstance(page[currentPage][choiceNum], Item):
                                            page[currentPage][choiceNum].tracker(amount, "Add", player)
                                        elif isinstance(page[currentPage][choiceNum], Sigil):
                                            player.reserveSigils.append(page[currentPage][choiceNum])
                                        if coins:
                                            player.coins -= price
                                        else:
                                            player.gamePoints -= price
                                        break

                                    elif choice == "2":
                                        break
                else:
                    return  "Continue"
         
        if currentTile["type"] == "buddyShop" and player.level >= 5:
            while True:
                clear() 
                print(f"{self.name} Training Shop")
                line("buddyOther")
                page = [Item.allItems["Pet Food Small"], Item.allItems["Pet Food Medium"], Item.allItems["Strength Treat"], Item.allItems["Cool Treat"], Item.allItems["Hastey Treat"]]
                
                number = 0
                for item in page[:]:
                    if isinstance(item, Item):
                        current = next((i for i in player.items if i.name == item.name), item)
                        print(f"{number}. {Color['yellow']}{item.name} | {current.playerAmount}/{item.maxAmount} | {item.gpCost}{Color['reset']}")
                        print(f"{Color['green']}{item.effect}{Color['reset']}")
                    number += 1
                    line("buddyOther")
                print("")
                
                line("buddyOther")
                print(f"Game Points: {Color['cyan']}{player.gamePoints}{Color['reset']}")
                print(f"{Color['red']}Type 'Exit' To Leave{Color['reset']}")
                line("buddyOther")
                                
                choice = input("$>")
                if choice in ["Exit", "exit"]:
                    return "Continue"
                    
                if choice.isdigit():
                    choice = int(choice)
                    if 0 <= choice <= len(page) - 1:
                        choiceNum = int(choice)
                        print(f"1. {Color['cyan']}GP{Color['reset']} | 2. {Color['red']}Back{Color['reset']}")
                        points = False
                        amount = False
                        purchase = False

                        while True:
                            choice = input("?>")
                            if choice == "1":
                                points = True
                                break
                            elif choice == "2":
                                break
                        
                        if points:
                            amount = True
                            price = page[choiceNum].gpCost

                        if amount:
                            while True:
                                print(f"How Many?") 
                                amount = input(f"{page[choiceNum].maxAmount}\\")
                                if amount and amount.isdigit():
                                    amount = int(amount)
                                    if amount != 0:
                                        i = next((s for s in player.items if s.name == page[choiceNum].name), page[choiceNum]).playerAmount
                                        if not amount + i > page[choiceNum].maxAmount:
                                            price = page[choiceNum].gpCost * amount
                                            purchase = True
                                            break
                                        else:
                                            print(f"{Color['red']}Exceeds Max Amount!{Color['reset']}")
                                            input(">")
                                            break
                        
                        if purchase:
                            while True:
                                print(f"{price} For {amount} {page[choiceNum].name}?")
                                print(f"1. {Color['green']}Yes{Color['reset']} 2. {Color['red']}No{Color['reset']}")

                                choice = input("?>")

                                if choice == "1":
                                    if points and player.gamePoints < price:
                                        print(f"{Color['red']}Not Enough GP!{Color['reset']}")
                                        input("?>")
                                        break
                                    if isinstance(page[choiceNum], Item):
                                        page[choiceNum].tracker(amount, "Add", player)
                                    player.gamePoints -= price
                                    break

                                elif choice == "2":
                                    break              
        
        elif currentTile["type"] == "boss":
            while True:
                clear()

                print(f"{Color['red']}Battle {currentTile['hazard'].name}?{Color['reset']}")
                line("battle")

                print(f"1. {Color['green']}Yes{Color['reset']}",
                    f"2. {Color['red']}No{Color['reset']}")
                line("battle")

                choice = input("->")
                if choice == "1":
                    clear()
                    line("battle")
                    print(f"{Color['red']}Boss Encounter!{Color['reset']}")
                    line("battle")

                    result = self.bossEncounter(player, copy.deepcopy(currentTile["hazard"]))

                    if result == "Win":
                        currentTile["type"] = "safe"
                        currentTile["hazard"] = None
                        player.savedMaps[player.location] = self
                        return "Win"

                    elif result in ["Loss", "Escape"]:
                        return result

                elif choice == "2":
                    return "Continue"

        elif currentTile["type"] == "raidBoss":
            while True:
                clear()

                print(f"{Color['red']}Battle {currentTile['hazard'].name}?{Color['reset']}")
                line("battle")

                print(f"1. {Color['green']}Yes{Color['reset']}",
                    f"2. {Color['red']}No{Color['reset']}")
                line("battle")

                choice = input("->")
                if choice == "1":
                    clear()
                    line("battle")
                    print(f"{Color['red']}Raid Encounter!{Color['reset']}")
                    line("battle")

                    result = self.bossEncounter(player, copy.deepcopy(currentTile["hazard"]))

                    if result == "Win":
                        currentTile["type"] = "safe"
                        currentTile["hazard"] = None
                        return "Win"

                    elif result == "Loss":
                        return "Loss"

                elif choice == "2":
                    return "Continue"
        
        elif currentTile["type"] == "train":
            def giveReward(player, pool):
                valid = []
                for item in pool:
                    if isinstance(item, Sigil):
                        if any(item.name == s.name for s in player.sigils + player.reserveSigils):
                            continue
                    elif isinstance(item, Skill):
                        if any(item.name == s.name for s in player.skills + player.reserveSkills):
                            continue
                    valid.append(item)
                if not valid:
                    return
                
                chosen = random.choice(valid)
                print(f"{Color['yellow']}{player.name} Got {chosen.name}!{Color['reset']}")

                if isinstance(chosen, Sigil):
                    player.reserveSigils.append(chosen)
                elif isinstance(chosen, Skill):
                    player.reserveSkills.append(chosen)

            currentPage = 1
            while True:
                clear()
                
                for stat in ["maxHealth", "maxMana", "strength", "magic", "defense", "resistance", "luck", "hit", "speed"]:
                    if stat == "maxHealth": setattr(player, stat, getattr(player, f"sigillessMaxHealth")); continue
                    if stat == "maxMana": setattr(player, stat, getattr(player, f"sigillessMaxMana")); continue       
                    setattr(player, stat, getattr(player, f"sigilless{stat.capitalize()}"))
                for equipped in player.sigils:
                    for stat, amount in equipped.statChange: setattr(player, stat, getattr(player, stat) + amount)
                for stat in ["maxHealth", "maxMana", "strength", "magic", "defense", "resistance", "luck", "hit", "speed"]:
                    if stat != "speed": setattr(player, stat, max(1, getattr(player, stat)))
                    else: setattr(player, stat, max(5, getattr(player, stat)))
                
                wave = [False, 1, self.scaling, currentTile["hazard"][2]]
                seassons = ["summer", "winter", "fall", "spring"]
                battle = False

                print(f"Training Hall | Level Rec: {self.scaling[0]}-{self.scaling[1]}")
                line("train")

                if currentPage == 1:
                    print(f"1. {Color['red']}Basic Training{Color['reset']}\n"
                        f"2. {Color['yellow']}Consecutive Training{Color['reset']}\n"
                        f"3. {Color['blue']}Timed Training{Color['reset']}\n"
                        f"4. {Color['magenta']}Extreme Training{Color['reset']}\n"
                        "5. Next Page")
                    print(f"6. {Color['yellow']}Training Shop{Color['reset']}")
                    print(f"7. {Color['yellow']}Rewards{Color['reset']}")
                    
                elif currentPage == 2:
                    print(f"1. {Color['red']}Cheater Training{Color['reset']}\n"
                        f"2. {Color['blue']}Survival Training{Color['reset']}\n"
                        f"3. {Color['yellow']}Seasson Training{Color['reset']}\n"
                        f"4. {Color['magenta']}Gauntlet Training{Color['reset']}\n"
                        "5. Previous Page")
                    
                    if player.level >= 10:
                        print(f"6. {Color['yellow']}Stat Boons{Color['reset']}")

                    if player.level >= 5:
                        print(f"7. {Color['cyan']}Buddy Shop{Color['reset']}")
                        
                print(f"8. {Color['red']}Exit{Color['reset']}")
                line("train")
                print("")

                print(player.name)
                line("train")

                # Health Bar
                meter = ""
                maxBars = 5
                barSize = player.maxHealth / maxBars

                for i in range(maxBars):
                    threshold = (i + 1) * barSize
                    if player.health >= threshold:
                        meter += f"{Color['red']}▮{Color['reset']}"
                    else:
                        meter += f"{Color['red']}▯{Color['reset']}"
                print(f"Health: {player.health} | {meter}")

                # Mana Bar 
                meter = ""
                maxBars = 5
                barSize = player.maxMana / maxBars

                for i in range(maxBars):
                    threshold = (i + 1) * barSize

                    if player.mana >= threshold:
                        meter += f"{Color['blue']}▮{Color['reset']}"
                    else:
                        meter += f"{Color['blue']}▯{Color['reset']}"
                print(f"Mana: {player.mana} | {meter}")

                # EXP Bar
                meter = ""
                maxBars = 5
                barSize = player.levelGoal / maxBars
                for i in range(maxBars):
                    threshold = (i + 1) * barSize
                    if player.levelValue >= threshold:
                        meter += f"{Color['yellow']}▮{Color['reset']}"
                    else:
                        meter += f"{Color['yellow']}▯{Color['reset']}"
                print(f"{player.level}: {meter}")
                
                print(f"Coins: {Color['yellow']}{player.coins}{Color['reset']}")
                print(f"Game Points: {Color['yellow']}{player.gamePoints}{Color['reset']}")
                line("train")

                choice = input("->")

                if choice in ["1", "2", "3", "4"]:
                    while True:
                        clear()

                        print("Go Through With Training?")
                        line("train")

                        print(f"1. {Color['green']}Yes{Color['reset']}",
                              f"2. {Color['red']}No{Color['reset']}")
                        line("train")

                        c = input("->")
                        if c == "1":
                            battle = True
                            break
                        elif c == "2":
                            break
                
                    if battle:
                        #-# Page 1 #-#
                        # Normal 
                        if choice == "1" and currentPage == 1:
                            result = self.enemyScale(player, "Normal", specialBattle=True)

                            if result == "Win":
                                reward = "Normal"
                        
                        # Consecutive 
                        elif choice == "2" and currentPage == 1:
                            repeat = currentTile["hazard"][0]()
                            wave[1] = 0
                            for i in range(1, repeat + 1):
                                clear()

                                line("battle")
                                print(f"{Color['red']}Battle {i}/{repeat}!{Color['reset']}")
                                line("battle")
                                input("?>")

                                result = self.enemyScale(player, "Consecutive", specialBattle=True)
                                if result in ["Loss", "Consecutive"]:
                                    break
                                wave[1] += 1
                                player.health += round(player.maxHealth * 0.25)
                                player.mana += round(player.maxMana * 0.25)
                                
                                if player.health >= player.maxHealth: player.health = player.maxHealth

                                if player.mana >= player.maxMana: player.mana = player.maxMana
                                reward = "Consecutive"

                        # Timed 
                        elif choice == "3" and currentPage == 1:
                            result = self.enemyScale(player, "Timed", True, currentTile["hazard"][1](), specialBattle=True)
                            if result == "Win":
                                reward = "Timed"

                        # Extreme/Boss  (Amplified)
                        elif choice == "4"  and currentPage == 1:
                            result = self.enemyScale(player, "Extreme", extreme=[True, currentTile["hazard"][2]], specialBattle=True)
                            if result == "Win":
                                reward = "Extreme"
                        
                        #-# Page 2 #-#
                        # Cheater 
                        if choice == "1" and currentPage == 2:
                            result = self.enemyScale(player, "Cheater", cheater=True, specialBattle=True)
                            if result == "Win":
                                reward = "Cheater"

                        # Survival 
                        if choice == "2" and currentPage == 2:
                            result = ""
                            wave[0] = True
                            while result not in ["Loss", "Escape"]:
                                clear()

                                line("battle")
                                print(f"{Color['red']}Battle {wave[1]}!{Color['reset']}")
                                line("battle")
                                input("?>")

                                result = self.enemyScale(player, "Survival", wave=wave, specialBattle=True)
                                if result in ["Loss", "Escape"] and wave[1] > 1:
                                    result = "Win"
                                    break
                                wave[1] += 1
                                if wave[1] % 5 == 0:
                                    wave[2][0] += 1
                                    wave[2][1] += 1
                            reward = "Survival"
                        
                        # Seasson 
                        if choice == "3" and currentPage == 2:
                            theme = random.choice(seassons)

                            if theme == "summer":
                                color = "red"
                                boss = "Sol"
                                desc = "Summer: After acting, gain Burn, Heated if Burn is at Max Stacks.\nFire skills have a chance to inflict Sear on either the user or opposer."
                            elif theme == "winter":
                                color = "blue"
                                boss = "White Silence"
                                desc = "Winter: After acting, there is a small chance to Gain Deep Freeze.\nIf any Chill statuses are present, chance to gain Frai II/Cripple I.\nIce skills always inflict Freeze."
                            elif theme == "fall":
                                color = "yellow"
                                boss = "Super Charged Slime"
                                desc = "Fall: After acting, gain either of; Shock, Overload, or Static.\nBased on the number of Shock statuses present, gain Boost I/Boost II/Boost III.\nThunder skills always inflict Static."
                            elif theme == "spring":
                                color = "magenta"
                                boss = "Syzoth"
                                desc = "Spring: After acting; gain 1 Poison or Bleed status, Poison statuses count (turns active) increase by 2, and chance to retrigger Bleed/Poison statuses.\nWind skills have a chance to inflict a Bleed status on the opposer."
                            rate = 1 if player.level <= 6 else 2 if player.level > 6 and player.level <= 12 else 3
                            
                            result = ""
                            number = 1
                            while result != "Loss":
                                clear()

                                line("battle")
                                print(f"{Color[color]}Battle {number}!{Color['reset']}")
                                print(f"{Color[color]}{desc}{Color['reset']}")
                                line("battle")
                                input("?>")

                                if number >= 5:
                                    result = self.enemyScale(player, "Seasson Boss", theme=[theme, number, boss, rate], specialBattle=True)
                                    if result == "Win": 
                                        reward = "Seasson"
                                    break

                                result = self.enemyScale(player, "Seasson Wave", theme=[theme, number, boss, rate], specialBattle=True)
                                if result == "Loss": break
                                number += 1

                                player.health += round(player.maxHealth * 0.25)
                                player.mana += round(player.maxMana * 0.25)
                                if player.health >= player.maxHealth: player.health = player.maxHealth
                                if player.mana >= player.maxMana: player.mana = player.maxMana

                        # Gauntlet Battles
                        if choice == "4" and currentPage == 2:
                            for i in range (len(currentTile["hazard"][2])):
                                result = self.enemyScale(player, "Gauntlet", extreme=[True, [currentTile["hazard"][2][i]]], specialBattle=True)

                                if player.health <= 0:
                                    break
                            if result == "Win":
                                reward = "Gauntlet"

                        if result == "Win":
                            player.health = player.maxHealth
                            player.mana = player.maxMana
                            
                            clear()

                            line("trainReward")
                            # Normal Battles
                            if reward not in ["Extreme", "Gauntlet", "Seasson"]:
                                coinReward = (random.randint(self.rewards["Coin/Exp"][0], self.rewards["Coin/Exp"][1]) * 2) * wave[1]
                                expReward = (random.randint(self.rewards["Coin/Exp"][0], self.rewards["Coin/Exp"][1])) * wave[1]
                                print(f"{Color['yellow']}{player.name} Got {coinReward} Coins!{Color['reset']}")
                                print(f"{Color['cyan']}{player.name} Got {expReward} EXP!{Color['reset']}")
                                player.coins += coinReward
                                player.levelValue += expReward

                            if reward in ["Normal", "Consecutive", "Timed", "Extreme", "Cheater", "Seasson", "Gauntlet"] and random.randint(1,100) >= 25:
                                pointsReward = ((random.randint(self.rewards["Game Point"][0], self.rewards["Game Point"][1]) + random.randint(1,2)) * wave[1]) * 5
                                print(f"{Color['cyan']}{player.name} Got {pointsReward} GP!{Color['reset']}")
                                player.gamePoints += pointsReward

                            if reward in ["Timed", "Extreme", "Consecutive", "Cheater", "Seasson", "Survival", "Gauntlet"] and random.randint(1,100) >= 15:
                                amount = random.randint(1,5)
                                chosen = random.choice(self.rewards["Items"])
                                print(f"{Color['yellow']}{player.name} Got {amount} {chosen.name}s!{Color['reset']}")
                                chosen.tracker(amount, "Add", player)

                            if reward == "Survival":
                                pointsReward = ((random.randint(self.rewards["Game Point"][0], self.rewards["Game Point"][1]) + random.randint(1,2)) * wave[1]) * 8
                                print(f"Survival Clause! {player.name} Got {pointsReward} GP!")
                                player.gamePoints += pointsReward
                                
                            if reward == "Cheater":
                                giveReward(player, self.rewards["Extreme"])
                                pointsReward = (random.randint(self.rewards["Game Point"][0], self.rewards["Game Point"][1]) + random.randint(1,2)) * random.randint(1, 3)
                                print(f"Cheater Clause! {player.name} Got {pointsReward} GP!")
                                player.gamePoints += pointsReward
                            
                            if reward in ["Extreme", "Seasson", "Gauntlet"] and random.randint(1, 100) >= 45:
                                giveReward(player, self.rewards["Extreme"])
                                pointsReward = (random.randint(self.rewards["Game Point"][0], self.rewards["Game Point"][1]) + random.randint(1,2)) * 6
                                print(f"{Color['red']}Extreme Clause! {player.name} Got {pointsReward} GP!{Color['reset']}")
                                player.gamePoints += pointsReward

                            if reward == "Gauntlet":
                                giveReward(player, self.rewards["Gauntlet"])
                                pointsReward = (random.randint(self.rewards["Game Point"][0], self.rewards["Game Point"][1]) + random.randint(1,2)) * 10
                                print(f"{Color['magenta']}Gauntlet Clause! {player.name} Got {pointsReward} GP!{Color['reset']}")
                                player.gamePoints += pointsReward

                            if reward == "Seasson":
                                giveReward(player, self.rewards["Seasson"])
                                pointsReward = (random.randint(self.rewards["Game Point"][0], self.rewards["Game Point"][1]) + random.randint(1,2)) * 8
                                print(f"{Color['yellow']}Seasson Clause! {player.name} Got {pointsReward} GP!{Color['reset']}")
                                player.gamePoints += pointsReward
                            
                            if reward in["Extreme", "Gauntlet", "Seasson"]:
                                coinReward = random.randint(self.rewards["Coin/Exp"][0], self.rewards["Coin/Exp"][1]) * 5
                                expReward = random.randint(self.rewards["Coin/Exp"][0], self.rewards["Coin/Exp"][1]) * 3
                                print(f"{Color['red']}Special Clause! {player.name} Got {coinReward} Coins!{Color['reset']}")
                                print(f"{Color['red']}Special Clause! {player.name} Got {expReward} EXP!{Color['reset']}")
                                player.coins += coinReward
                                player.levelValue += expReward
                            
                            line("trainReward")
                            input("?>")

                        elif result == "Loss":
                            if player.health <= 0:
                                player.health = round(player.maxHealth * 0.30)
                            
                            if player.mana <= 0:
                                player.mana = round(player.maxMana * 0.30)

                if choice == "5" and currentPage == 1:
                    currentPage +=1
                
                elif choice == "5" and currentPage == 2:
                    currentPage -=1

                if choice == "6" and currentPage == 1:
                    currentPage = 0

                    while True:
                        clear()

                        print(f"{self.name} Training Shop")
                        line("shopTrain")
                        
                        rewards = self.rewards["Extreme"] + self.rewards["Gauntlet"] + self.rewards["Seasson"]
                        page = [[Item.allItems["Experience Page"], Item.allItems["Experience Book"], Item.allItems["Experience Tome"]]]
                        for item in rewards:
                            if isinstance(item, Sigil):
                                if any(item.name == s.name for s in player.sigils + player.reserveSigils):
                                    continue
                            if isinstance(item, Skill):
                                if any(PlayerSkill.allScrolls[item.name].skill.name == s.name for s in player.skills + player.reserveSkills) or any(PlayerSkill.allScrolls[item.name].name == i.name for i in player.items):
                                    continue 
                            if not page or len(page[-1]) == 5:
                                page.append([])
                            page[-1].append(item)
                        if page and currentPage >= len(page):
                            currentPage = len(page) - 1
                        
                        if page:
                            number = 0
                            for item in page[currentPage][:]:
                                if isinstance(item, Sigil):
                                    print(f"{number}. {Color['yellow']}{item.name} | {item.affinity} | {item.gpCost} GP{Color['reset']}")
                                    print(f"{Color['green']}{item.effect}{Color['reset']}")
                                elif isinstance(item, Skill):
                                    print(f"{number}. {Color['yellow']}{PlayerSkill.allScrolls[item.name].name} | {PlayerSkill.allScrolls[item.name].playerAmount}/{PlayerSkill.allScrolls[item.name].maxAmount} | {PlayerSkill.allScrolls[item.name].gpCost * 2} GP{Color['reset']}")
                                    print(f"{Color['green']}{PlayerSkill.allScrolls[item.name].effect}{Color['reset']}")
                                    page[currentPage] = [PlayerSkill.allScrolls[item.name] if isinstance(i, Skill) and i.name == PlayerSkill.allScrolls[item.name].skill.name else i for i in page[currentPage]]
                                elif isinstance(item, Item):
                                    current = next((i for i in player.items if i.name == item.name), item)
                                    print(f"{number}. {Color['yellow']}{item.name} | {current.playerAmount}/{item.maxAmount} | {item.gpCost * 2}{Color['reset']}")
                                    print(f"{Color['green']}{item.effect}{Color['reset']}")
                                number += 1
                                line("shopTrain")
                            print("")

                            line("shopTrain")
                            print(f"Game Points: {Color['cyan']}{player.gamePoints}{Color['reset']}")
                            print(f"{Color['red']}Type 'Exit' To Leave{Color['reset']}")
                            if currentPage + 1 < len(page): print("Type 'Next' For Next Page")
                            if currentPage > 0: print("Type 'Pre' For Previous Page")
                            line("shop")
                            
                            choice = input("$>")
                            if choice in ["Exit", "exit"]:
                                return "Continue"

                            if choice in ["Next", "next"] and currentPage + 1 < len(page):
                                currentPage += 1

                            if choice in ["Pre", "pre"] and currentPage > 0:
                                currentPage -= 1

                            if choice.isdigit():
                                choice = int(choice)
                                if 0 <= choice <= len(page[currentPage]) - 1:
                                    choiceNum = int(choice)
                                    print(f"1. {Color['cyan']}GP{Color['reset']} | 2. {Color['red']}Back{Color['reset']}")
                                    points = False
                                    purchase = False

                                    while True:
                                        choice = input("?>")
                                        if choice == "1":
                                            points = True
                                            break
                                        elif choice == "2":
                                            break
                                    
                                    if points:
                                        purchase = True
                                        price = page[currentPage][choiceNum].gpCost
                                        if isinstance(page[currentPage][choiceNum], Item):
                                            price *= 2

                                    if purchase:
                                        while True:
                                            print(f"{price} For {page[currentPage][choiceNum].name}?")
                                            print(f"1. {Color['green']}Yes{Color['reset']} 2. {Color['red']}No{Color['reset']}")

                                            choice = input("?>")

                                            if choice == "1":
                                                if points and player.gamePoints < price:
                                                    print(f"{Color['red']}Not Enough GP!{Color['reset']}")
                                                    input("?>")
                                                    break
                                                if isinstance(page[currentPage][choiceNum], Item):
                                                    page[currentPage][choiceNum].tracker(1, "Add", player)
                                                elif isinstance(page[currentPage][choiceNum], Sigil):
                                                    player.reserveSigils.append(page[currentPage][choiceNum])
                                                player.gamePoints -= price
                                                break

                                            elif choice == "2":
                                                break
                
                if choice == "6" and currentPage == 2 and player.level >= 10:
                    while True:
                        clear()
                        
                        print("Stat Modifier")
                        line("statModifier")
                        
                        print(f"Max Health Modifiers: {Color['yellow']}{sum(1 for s in player.modifiers if s[0] == 'MaxHealth')}{Color['reset']} | Base: {Color['red']}{player.sigillessMaxHealth}{Color['reset']}")
                        print(f"Max Mana Modifiers: {Color['yellow']}{sum(1 for s in player.modifiers if s[0] == 'MaxMana')}{Color['reset']} | Base: {Color['blue']}{player.sigillessMaxMana}{Color['reset']}")
                        
                        for stat in ["strength", "magic", "defense", "resistance", "speed", "luck", "hit"]:
                            sigilless = getattr(player, f'sigilless{stat.capitalize()}')
                            total = sum(s[1] for s in player.modifiers if s[0] == stat)
                            print(f"{stat.capitalize()} Modifiers: {Color['yellow']}{total}{Color['reset']} | Base: {Color['green']}{sigilless}{Color['reset']}")
                        line("statModifier")
                        print("")
                        
                        print(f"Utility: {Color['yellow']}{player.utl}/3{Color['reset']}")
                        print(f"Vital: {Color['red']}{player.vit}/4{Color['reset']}")
                        print(f"Body: {Color['cyan']}{player.bdy}/10{Color['reset']}")
                        line("statModifier")
                        print("")
                        
                        print(f"GP: {Color['cyan']}{player.gamePoints}{Color['reset']}")
                        line("statModifier")
                        print("")
                        
                        utlPrice = round(5000 * (1 + player.utl / 10))
                        vitPrice = round(4000 * (1 + player.vit / 10))
                        bdyPrice = round(3000 * (1 + player.bdy / 10))
                        
                        line("statModifier")
                        print(f"1. {Color['yellow']}Modify Utility{Color['reset']} | {Color['cyan']}{utlPrice}{Color['reset']} GP")
                        print(f"2. {Color['red']}Modify Vital{Color['reset']} | {Color['cyan']}{vitPrice}{Color['reset']} GP")
                        print(f"3. {Color['cyan']}Modify Body{Color['reset']} | {Color['cyan']}{bdyPrice}{Color['reset']} GP")
                        print(f"4. {Color['red']}Reset Modifiers{Color['reset']} | {Color['magenta']}Only 30% of GP Spent Will Be Refunded!{Color['reset']}")
                        print("5. Exit")
                        line("statModifier")
                        
                        choice = input("?>")
                        
                        if choice == "1":
                            if not player.utl >= 3:
                                line("statModifier")
                                print(f"1. {Color['yellow']}Speed{Color['reset']} | 2. {Color['yellow']}Luck{Color['reset']} | 3.{Color['yellow']}Hit{Color['reset']} | 4. Back")
                                line("statModifier")
                                
                                while True:
                                    choice = input("?>")
                                    
                                    if choice in ["1", "2", "3"]:
                                        stats = ["speed", "luck", "hit"]
                                        if player.gamePoints >= utlPrice:
                                            setattr(player, f"sigilless{stats[int(choice) - 1].capitalize()}", getattr(player, f"sigilless{stats[int(choice) - 1].capitalize()}") + 5)
                                            print(f"{Color['yellow']}{stats[int(choice) - 1].capitalize()} Increased By 5!{Color['reset']}")
                                            player.modifiers.append([stats[int(choice) - 1], 5, utlPrice])
                                            player.utl += 1
                                            player.gamePoints -= utlPrice
                                            input(">")
                                            break
                                        
                                        else:
                                            print(f"{Color['red']}Not Enough GP!{Color['reset']}")
                                            input(">")
                                            break
                                    
                                    elif choice == "4":
                                        break
                            
                            else:
                                print(f"{Color['red']}Max Amount Of Utility Modifiers Reached!{Color['reset']}")
                                input(">")
                        
                        elif choice == "2":
                            if not player.vit >= 4:
                                line("statModifier")
                                print(f"1. {Color['red']}Health{Color['reset']} | 2. {Color['blue']}Mana{Color['reset']} | 3. Back")
                                line("statModifier")
                                
                                while True:
                                    choice = input("?>")
                                    
                                    if choice in ["1", "2"]:
                                        stats = ["MaxHealth", "MaxMana"]
                                        if player.gamePoints >= vitPrice:
                                            setattr(player, f"sigilless{stats[int(choice) - 1]}", getattr(player, f"sigilless{stats[int(choice) - 1]}") + (100 if stats[int(choice) - 1] == "MaxHealth" else 50))
                                            print(f"{Color['yellow']}{'Health' if stats[int(choice) - 1] == "MaxHealth" else 'Mana'} Increased By {'100' if stats[int(choice) - 1] == "MaxHealth" else '50'}!{Color['reset']}")
                                            player.modifiers.append([stats[int(choice) - 1],(100 if stats[int(choice) - 1] == "MaxHealth" else 50), vitPrice])
                                            player.vit += 1
                                            player.gamePoints -= vitPrice
                                            input(">")
                                            break
                                        
                                        else:
                                            print(f"{Color['red']}Not Enough GP!{Color['reset']}")
                                            input(">")
                                            break
                                    
                                    elif choice == "3":
                                        break
                            
                            else:
                                print(f"{Color['red']}Max Amount Of Vitality Modifiers Reached!{Color['reset']}")
                                input(">")
                        
                        elif choice == "3":
                            if not player.bdy >= 10:
                                line("statModifier")
                                print(f"1. {Color['cyan']}Strength{Color['reset']} | 2. {Color['cyan']}Magic{Color['reset']} | 3.{Color['cyan']}Defense{Color['reset']} | 4. {Color['cyan']}Resistance{Color['reset']} | 5. Back")
                                line("statModifier")
                                
                                while True:
                                    choice = input("?>")
                                    
                                    if choice in ["1", "2", "3", "4"]:
                                        stats = ["strength", "magic", "defense", "resistance"]
                                        if player.gamePoints >= bdyPrice:
                                            setattr(player, f"sigilless{stats[int(choice) - 1].capitalize()}", getattr(player, f"sigilless{stats[int(choice) - 1].capitalize()}") + 5)
                                            print(f"{Color['yellow']}{stats[int(choice) - 1].capitalize()} Increased By 3!{Color['reset']}")
                                            player.modifiers.append([stats[int(choice) - 1], 3, bdyPrice])
                                            player.bdy += 1
                                            player.gamePoints -= bdyPrice
                                            input(">")
                                            break
                                        
                                        else:
                                            print(f"{Color['red']}Not Enough GP!{Color['reset']}")
                                            input(">")
                                            break
                                    
                                    elif choice == "5":
                                        break
                            
                            else:
                                print(f"{Color['red']}Max Amount Of Body Modifiers Reached!{Color['reset']}")
                                input(">")
                        
                        elif choice == "4" and len(player.modifiers) > 0:
                            refund = 0
                            for modifier in player.modifiers:
                                refund += modifier[2]
                            refund = round(refund * 0.3)
                            line("statModifier")
                            print(f"1. {Color['green']}Remove All Modifiers (Gain {Color['cyan']}{refund}{Color['reset']} GP){Color['reset']} | 2. Back")
                            line("statModifier")
                            
                            while True:
                                choice = input("?>")
                                
                                if choice == "1":
                                    for modifier in player.modifiers:
                                        if modifier[0] in ["speed", "luck", "hit"]:
                                            player.utl -= 1
                                            setattr(player, f"sigilless{modifier[0].capitalize()}", getattr(player, f"sigilless{modifier[0].capitalize()}") - modifier[1])
                                            setattr(player, modifier[0], getattr(player, modifier[0]) - modifier[1])
                                            
                                        if modifier[0] in ["MaxHealth", "MaxMana"]:
                                            player.vit -= 1
                                            setattr(player, f"sigilless{modifier[0]}", getattr(player, f"sigilless{modifier[0]}") - modifier[1])
                                            if modifier[0] == "MaxHealth": setattr(player, modifier[0], getattr(player, "maxHealth") - modifier[1])
                                            if modifier[0] == "MaxMana": setattr(player, modifier[0], getattr(player, "maxMana") - modifier[1])
                                                                                    
                                        if modifier[0] in ["strength", "magic", "defense", "resistance"]:
                                            player.bdy -= 1
                                            setattr(player, f"sigilless{modifier[0].capitalize()}", getattr(player, f"sigilless{modifier[0].capitalize()}") - modifier[1])
                                            setattr(player, modifier[0], getattr(player, modifier[0]) - modifier[1])
                                            
                                    if player.utl < 0: player.utl = 0
                                    if player.vit < 0: player.vit = 0
                                    if player.bdy < 0: player.bdy = 0
                                    
                                    player.modifiers = []
                                    player.gamePoints += refund
                                    break
                                
                                elif choice == "2":
                                    break
                        
                        elif choice == "5":
                            break
                        
                if choice == "7" and currentPage == 1:
                    clear()
                    rewards = [
                        ("Extreme", self.rewards["Extreme"]),
                        ("Gauntlet", self.rewards["Gauntlet"]),
                        ("Seasson", self.rewards["Seasson"])]

                    for rewardType, rewardList in rewards:
                        print(f"{Color['yellow']}{rewardType}{Color['reset']}")
                        line("trainReward")

                        if not rewardList:
                            print("None")
                        else:
                            for reward in rewardList:
                                print(f"{reward.name}")
                                if hasattr(reward, "family"):
                                    print(f"{Color['green']}{reward.family}{Color['reset']}")
                                if hasattr(reward, "effect") and not isinstance(reward, Skill):
                                    print(f"{Color['cyan']}{reward.effect}{Color['reset']}")
                                if hasattr(reward, "text"):
                                    print(f"{Color['cyan']}{reward.text}{Color['reset']}")
                                line("train")
                        print("")
                    input("?>")

                if choice == "7" and currentPage == 2 and player.level >= 5:
                    currentPage = 0

                    while True:
                        clear()

                        print(f"{self.name} Buddy Shop")
                        line("shopTrain")
                        
                        page = []
                        ownedBuddies = [b for b in [player.buddy] + player.reserveBuddies if b is not None]
                        for buddy in self.rewards["Buddy"]:
                            if ownedBuddies and any(Buddy.allBuddies[buddy.name].name == b.name for b in ownedBuddies):
                                continue 
                            if not page or len(page[-1]) == 3:
                                page.append([])
                            page[-1].append(buddy)
                        if page and currentPage >= len(page):
                            currentPage = len(page) - 1
                        
                        if page:
                            number = 0
                            for buddy in page[currentPage][:]:
                                print(f"{number}. {Color['cyan']}{buddy.name} {Color['reset']}|{Color['cyan']} {buddy.affinity}{Color['reset']}")
                                print(f"{Color['cyan']}Attack: {buddy.attack} {Color['reset']}|{Color['cyan']} Talent: {buddy.talent} {Color['reset']}|{Color['cyan']} Speed: {buddy.speed}{Color['reset']}")
                                text = Color['yellow'] + buddy.passive.text + Color['reset']
                                names = sorted(Status.allStatuses.keys(), key=len, reverse=True)
                                pattern = r"\b(" + "|".join(map(re.escape, names)) + r")\b"
                                text = re.sub(pattern, lambda m: colorize(m, Status), text)
                                print(f"{buddy.passive.name}: {text}")
                                
                                text = Color['magenta'] + buddy.skill.text + Color['reset']
                                names = sorted(Status.allStatuses.keys(), key=len, reverse=True)
                                pattern = r"\b(" + "|".join(map(re.escape, names)) + r")\b"
                                text = re.sub(pattern, lambda m: colorize(m, Status), text)
                                print(f"{buddy.skill.name}: {text} {f'| {Color['yellow']} Hit: {buddy.skill.hit} {Color['reset']} | {Color['yellow']} Critical: {buddy.skill.critical}' if 'Damage' in buddy.skill.type_ else ''} {Color['reset']}")
                                print(f"Price: {Color['cyan']}{buddy.gpCost}{Color['reset']} Game Points")
                                number += 1
                                line("shop")
                            print("")
        
                            line("shop")
                            print(f"Game Points: {Color['cyan']}{player.gamePoints}{Color['reset']}")
                            print(f"{Color['red']}Type 'Exit' To Leave{Color['reset']}")
                            if currentPage + 1 < len(page): print("Type 'Next' For Next Page")
                            if currentPage > 0: print("Type 'Pre' For Previous Page")
                            line("shop")
                            
                            choice = input("$>")
                            if choice in ["Exit", "exit"]:
                                return "Continue"
        
                            if choice in ["Next", "next"] and currentPage + 1 < len(page):
                                currentPage += 1
        
                            if choice in ["Pre", "pre"] and currentPage > 0:
                                currentPage -= 1
        
                            if choice.isdigit():
                                choice = int(choice)
                                if 0 <= choice <= len(page[currentPage]) - 1:
                                    choiceNum = int(choice)
                                    print(f"1. {Color['cyan']}GP{Color['reset']} | 2. {Color['red']}Back{Color['reset']}")
                                    points = False
                                    purchase = False
        
                                    while True:
                                        choice = input("?>")
                                        if choice == "1":
                                            points = True
                                            break
                                        elif choice == "2":
                                            break
                                    
                                    if points:
                                        price = int(page[currentPage][choiceNum].gpCost)
                                        purchase = True
        
                                    if purchase:
                                        while True:
                                            print(f"{price} For {page[currentPage][choiceNum].name}?")
                                            print(f"1. {Color['green']}Yes{Color['reset']} 2. {Color['red']}No{Color['reset']}")
        
                                            choice = input("?>")
        
                                            if choice == "1":
                                                if player.gamePoints < price:
                                                    print(f"{Color['red']}Not Enough GP!{Color['reset']}")
                                                    input("?>")
                                                    break
                                                
                                                player.reserveBuddies.append(copy.copy(page[currentPage][choiceNum]))
                                                player.gamePoints -= price
                                                break
        
                                            elif choice == "2":
                                                break
                                                
                        else: break
                        
                if choice == "8":
                    return "Continue"
        
        elif currentTile["type"] == "reward":
            for setS in currentTile["hazard"]:
                if isinstance(setS[0], Item):
                    print(f"{Color['yellow']}{player.name} Found {setS[1]} {setS[0].name}s!{Color['reset']}")
                    setS[0].tracker(setS[1], "Add", player)

                if isinstance(setS[0], PlayerSkill):
                    print(f"{Color['magenta']}{player.name} Found {PlayerSkill.allScrolls[setS[0].name].name}!{Color['reset']}")
                    player.items.append(PlayerSkill.allScrolls[setS[0].name])

                if isinstance(setS[0], Buddy):
                    print(f"{Color['cyan']}{player.name} Found The {setS[0].name} Buddy!{Color['reset']}")
                    player.reserveBuddies.append(copy.deepcopy(setS[0]))

                if isinstance(setS[0], Sigil):
                    print(f"{Color['cyan']}{player.name} Found The {setS[0].name}!{Color['reset']}")
                    player.reserveSigils.append(copy.deepcopy(setS[0]))
            currentTile["type"] = "safe"
            currentTile["hazard"] = None
            player.savedMaps[player.location] = self

        # Raid Only 
        elif currentTile["hazard"] == "spring":
            healthHeal = round(player.maxHealth * 0.15)
            manaHeal = round(player.maxMana * 0.20)
            player.health = min(player.maxHealth, player.health + healthHeal)
            player.mana = min(player.maxMana, player.mana + manaHeal)

            print(f"{Color['green']}{player.name} Healed {healthHeal} HP & {manaHeal} MP In A Hot Spring!{Color['reset']}")
            print("It Disappeared!")

            self.tiles[(player.y, player.x)]["hazard"] = None
            self.tiles[(player.y, player.x)]["type"] = "safe"
        
        elif currentTile["hazard"] == "wheatstone":
            offensive = random.randint(1,3)
            player.sigillessStrength += offensive
            player.sigillessMagic += offensive
            Status.allStatuses["Fix"].statMutation(player)

            print(f"{Color['yellow']}{player.name} Sharpened A Sword With A Wheatstone! Their Offensive Stats Increased By {offensive}!{Color['reset']}")        
            print("It Disappeared!")

            self.tiles[(player.y, player.x)]["hazard"] = None
            self.tiles[(player.y, player.x)]["type"] = "safe"

        elif currentTile["hazard"] == "forge":
            defensive = random.randint(1,2)
            player.sigillessDefense += defensive
            player.sigillessResistance += defensive
            Status.allStatuses["Fix"].statMutation(player)

            print(f"{Color['yellow']}{player.name} Forged Themselvs Armor! Their Defensive Stats Increased By {defensive}!{Color['reset']}")        
            print("It Disappeared!")

            self.tiles[(player.y, player.x)]["hazard"] = None
            self.tiles[(player.y, player.x)]["type"] = "safe"

        return None
    
    # Raids
    def startRaid(self, player, raidMap):
        # raidMap should be normal_raid_maps passed into the function
        raidMap = copy.deepcopy(raidMap)

        # Creates copy of player to use in raid and emptys inventory
        raidPlayer = copy.deepcopy(player)
        raidPlayer.items = [] 
        raidPlayer.reserveSkills = []
        raidPlayer.reserveSigils = []
        raidPlayer.reserveBuddies = []
        raidPlayer.progress = 0

        # Starts raid copy to max
        raidPlayer.health = raidPlayer.maxHealth
        raidPlayer.mana = raidPlayer.maxMana
        
        # Remove 25% of Strength/Magic/Defense/Resistance
        raidPlayer.sigillessStrength -= round(raidPlayer.baseStrength * 0.25)
        raidPlayer.sigillessMagic -= round(raidPlayer.baseMagic * 0.25)
        raidPlayer.sigillessDefense -= round(raidPlayer.baseDefense * 0.25)
        raidPlayer.sigillessResistance -= round(raidPlayer.baseResistance * 0.25)
        # Using base Beacuse It Takes Sigils into consideration.

        # Cap Speed At 30
        raidPlayer.sigillessSpeed = min(30, raidPlayer.baseSpeed)
        Status.allStatuses["Fix"].statMutation(raidPlayer)

        # Random Maps
        maps = []
        while len(maps) < 3:
            chosen = random.choice(raidMap)
            raidMap.remove(chosen)

            chosen = Map.placements(chosen, raidPlayer, [Enemy.allEnemies["Blue Blur"], Enemy.allEnemies["Rookie S. Cop"], Enemy.allEnemies["Green Dino"]])
            maps.append(chosen)

        return raidPlayer, maps 

    def placements(map_, player, enemies, special=False):
        # Placements
        for (y, x), tile in map_.tiles.items():
            if not tile.get("raidTile") and not tile.get("raidEnemy"):
                continue

            # Boon Placements
            elif tile.get("raidTile"):
                pool = ["reward"] * 25 + ["spring"] * 8 + ["wheatstone"] * 2 + ["forge"] * 1
                chosenTile = random.choice(pool)
                if chosenTile == "reward":
                    if random.randint(1, 150) + player.luck // 2 > random.randint(1, 350):
                        # Reward Tiles
                        map_.tiles[(y, x)]["type"] = chosenTile
                        itemPool = [Item.allItems["Red M.Valens Potion"], Item.allItems["Blue M.Valens Potion"], Item.allItems["Cleanse M. Potion"], Item.allItems["Refined Dew"], Item.allItems["Heart Charm"]]
                        k = random.randint(1,3)
                        itemPool = random.sample(itemPool, k)
                        chosenItems = [[s, random.randint(1,3)] for s in itemPool]
                        map_.tiles[(y, x)]["hazard"] = chosenItems

                elif chosenTile == "spring":
                    map_.tiles[(y, x)]["hazard"] = chosenTile
                    map_.tiles[(y, x)]["type"] = "boon"

                elif chosenTile == "wheatstone":
                    map_.tiles[(y, x)]["hazard"] = chosenTile
                    map_.tiles[(y, x)]["type"] = "event"

                elif chosenTile == "forge":
                    map_.tiles[(y, x)]["hazard"] = chosenTile
                    map_.tiles[(y, x)]["type"] = "event"

            # Enemy Placements
            elif tile.get("raidEnemy"):
                # Raid Boss & Enemy
                if special:
                    enemy = copy.deepcopy(random.choice(enemies))
                    map_.tiles[(y, x)]["type"] = "raidBoss"
                    map_.tiles[(y, x)]["hazard"] = enemy

                # Generics
                else:
                    enemy = copy.deepcopy(random.choice(enemies))
                    # Create 5 Generic Raid Enemies
                    enemy.theme = random.choice(["leech", "dread"])
                    raidSkill = copy.deepcopy(random.choice([EnemySkill.allSkills["Lucky Play"], EnemySkill.allSkills["Monster"], EnemySkill.allSkills["Closed Off"]]))
                    raidSkill.tag = "raid"
                    enemy.skills.append(raidSkill) 
                    # This will be for the Raid only passives
                    map_.tiles[(y, x)]["type"] = "raidBoss"
                    map_.tiles[(y, x)]["hazard"] = enemy

        return map_

    ##--##
    
    def toDict(self):
        changedTiles = {}
        template = Map.allMaps.get(self.name)

        for pos, tile in self.tiles.items():
            templateTile = template.tiles.get(pos) if template else None

            originalType = templateTile["type"] if templateTile else None

            if originalType in ("boss", "reward") and tile["type"] == "safe":
                changedTiles[str(pos)] = {"type": "safe", "hazard": None}

            elif originalType in ["gate", "gateHaz", "gateNull"] and tile["type"] == "transition":
                changedTiles[str(pos)] = {"type": "transition", "hazard": tile["hazard"], "wallNorth": tile["wallNorth"], "wallSouth": tile["wallSouth"], "wallEast": tile["wallEast"], "wallWest": tile["wallWest"]}

            elif originalType == "train":
                hazard = tile["hazard"]
                if hazard != "BASE" and not callable(hazard):
                    changedTiles[str(pos)] = {"type": tile["type"], "hazard": "BASE"}

        return {"name": self.name, "version": self.version, "changedTiles": changedTiles}

    def fromDict(data):
        template = Map.allMaps[data["name"]]
        savedVersion = data.get("version", 1)

        if template.version > savedVersion:
            return copy.deepcopy(template)
    
        map_ = copy.deepcopy(Map.allMaps[data["name"]])

        for pos, tileData in data["changedTiles"].items():
            y, x = eval(pos)
            if tileData["type"] == "safe" and tileData["hazard"] is None:
                map_.tiles[(y, x)]["type"] = "safe"
                map_.tiles[(y, x)]["hazard"] = None

            if tileData["type"] == "transition" and map_.tiles[(y, x)]["type"] in ["gate", "gateHaz", "gateNull"]:
                map_.tiles[(y, x)]["type"] = "transition"

        return map_
    
    def movement(self, player, direction, GHOST=False):
        currentTile = self.tiles.get((player.y, player.x))

        if direction in "wW" and (not currentTile["wallNorth"] or GHOST):
            player.y -= 1

            player.y = max(1, min(player.y, self.maxY))
            self.tiles[(player.y, player.x)]["previous"] = "south"

        elif direction in "aA" and (not currentTile["wallWest"] or GHOST):
            player.x -= 1

            player.x = max(1, min(player.x, self.maxX))
            self.tiles[(player.y, player.x)]["previous"] = "east"

        elif direction in "sS" and (not currentTile["wallSouth"] or GHOST):
            player.y += 1

            player.y = max(1, min(player.y, self.maxY))
            self.tiles[(player.y, player.x)]["previous"] = "north"

        elif direction in "dD" and (not currentTile["wallEast"] or GHOST):
            player.x += 1

            player.x = max(1, min(player.x, self.maxX))
            self.tiles[(player.y, player.x)]["previous"] = "west"

    def transition(self, player, location, x, y):
        clear()
        print(f"{Color['magenta']}Travel To {location}!{Color['reset']}")
        line("basicOther")

        print(f"1. {Color['green']}Yes{Color['reset']}",
              f"2. {Color['red']}No{Color['reset']}")
        line("basic")

        choice = ""
        while choice not in ["1", "2"]:
            choice = input("->")
            if choice == "1":
                target = Map.allMaps.get(location)
                if target:
                    player.savedMaps[player.location] = self
                    player.location = location
                    player.x = x
                    player.y = y
                    return
                else:
                    clear()
                    print("Map Not Found. Dev Error. Loser.")
                    input("??>")

            elif choice == "2":
                break

    def gate(self, player, location, x, y, cost, current):
        clear()
        print(f"{Color['magenta']}Travel To {location}!{Color['reset']}")
        line("basicOther")

        print(f"1. {Color['green']}Yes{Color['reset']}",
              f"2. {Color['red']}No{Color['reset']}")
        print(f"GP Cost: {Color['cyan']}{cost}{Color['reset']}")
        line("basic")

        choice = ""
        while choice not in ["1", "2"]:
            choice = input("->")
            if choice == "1":
                if player.gamePoints >= cost:
                    player.gamePoints -= cost
                    self.tiles[player.y, player.x]["type"] = "transition"
                    if len(self.tiles[player.y, player.x]["hazard"][4]) >= 1:
                        for direction in self.tiles[player.y, player.x]["hazard"][4]:
                            self.tiles[player.y, player.x][direction] = True
                    target = Map.allMaps.get(location)
                    if target:
                        player.savedMaps[player.location] = self
                        player.location = location
                        player.x = x
                        player.y = y
                        return
                    else:
                        clear()
                        print("Map Not Found. Dev Error. Loser.")
                        input("??>")

                else:
                    print(f"{Color['red']}Not Enough GP!{Color['reset']}")
                    input("??>")
                    break

            elif choice == "2":
                break
        
    def display(self, player):
        tileSymbols = {
            "player": f"{Color['reset']}0{Color['reset']}",
            "safe": f"{Color['cyan']}@{Color['reset']}",
            "hazard": f"{Color['red']}X{Color['reset']}",
            "gateHaz": f"{Color['red']}X{Color['reset']}",
            "whirl": f"{Color['blue']}@{Color['reset']}",
            "boss": f"{Color['magenta']}!{Color['reset']}",
            "raidBoss": f"{Color['magenta']}!{Color['reset']}",
            "boon": f"{Color['green']}X{Color['reset']}",
            "shop": f"{Color['yellow']}${Color['reset']}",
            "buddyShop": f"{Color['red']}${Color['reset']}",
            "train": f"{Color['yellow']}!{Color['reset']}",
            "reward": f"{Color['green']}${Color['reset']}",
            "none": " ",
            "gateNull": " ",
            "transition": f"{Color['yellow']}#{Color['reset']}",
            "gate": f"{Color['cyan']}@{Color['reset']}",
            "storage": f"{Color['red']}Z{Color['reset']}",
            "event": f"{Color['yellow']}!{Color['reset']}",
            "raid": f"{Color['red']}R{Color['reset']}"
        }
        
        displayRow = []
        for y in range(1, self.maxY + 1):
            row = ""
            for x in range(1, self.maxX + 1):
                # Player Display
                if x == player.x and y == player.y:
                    row += tileSymbols["player"] + " | "
                
                # Other Display
                else:                        
                    tile = self.tiles.get((y, x))
                    symbol = tileSymbols.get(tile.get("type"))
                    row += symbol + " | "
            
            displayRow.append(row)
        
        return displayRow