from Utility import *

class Guide:
    guides = {}
    def __init__(self, title, display):
        self.title = title
        self.display = display
        Guide.guides[title] = display

guide_basics = (
    f"In Ruin Fountain, both the Player and Enemy share multiple attributes:\n"
    f"Health: When this stat reaches 0, the battle will conclude in either victory or a loss.\n"
    f"Strength: The main offensive stat for Physical type damaging skills.\n"
    f"Magic: The main offensive stat for Magic type damaginign skills.\n"
    f"Defense: The main defensive stat for Physical type damaginign skills.\n"
    f"Resistance: The main defensive stat for Magic type damaginign skills.\n"
    f"Luck: Determines evasion, escape and critical chance. If a skill uses this as its offensive stat, it is a Physical type damaging skill. {Color['cyan']}Note: Go to 4. Strike Types for more{Color['reset']}.\n"
    f"Hit: Determines whether an attack or certain skills land. Checks Hit against opposers Luck. If a skill uses this as its offensive stat, it is a Physical type damaging skill. {Color['cyan']}Note: Go to 4. Strike Types for more{Color['reset']}.\n"
    f"Speed: Determines how fast the Speed Meter fills. {Color['cyan']}Note: Go to 2. Batttle Info for more{Color['reset']}."
    )
guide_basics = Guide("The Basics", guide_basics)

guide_battle = (
    f"The battles of Ruin Fountain have many moving components, but the rules are simple:\n"
    f"1. If one of the battlers Health reaches 0, the battle will end. If the Players Health reaches 0 before or at the same time as the Enemy, that will result in a loss.\n"
    f"2. Battlers can act multiple times in a row as long as their Speed Meter can be filled within in time. {Color['cyan']}Note: Go to 3. Battle Meters for more{Color['reset']}."
    f"3. On defeat, the Player can retry a fight, only if the Enemy is a Boss. Otherwise, they will be returned to the main menu.\n"
    f"4. During Boss battles, escape is not an option."
    
    "\n\n=======\n\n"
    
    "In battle, the player will have 6 actions to chose from:\n"
    "1. Attack: A basic attack to the enemy that uses the highest offensive stat of the Player. Can land criticals and miss.\n"
    f"2. Skill: Actions that cost Mana and have cooldowns. {Color['cyan']}Note: Go to 7. Skills & 8. Equipables for more{Color['reset']}.\n"
    "3. Item: Consumable objects that restore Health and Mana, deal damage, or other effects without costing Mana or having a cooldown.\n"
    "4. Analyze: Displays informtaion about the Enemy. Their skills, ultimate skill, statuses, Speed Meter, etc. Importantly, it shows the Enemies elemental affinites.\n"
    "5. Escape: A Luck based option that gives the Player a way to end battles early if succesful.\n"
    "6. Wait: Pass on acting in a meaningful way. Has a chance to remove a Negative Status. At 75%/50% Health / Mana, restore 8%/15% of Health / Mana.\n"
    
    "\nThe Enemy can attack, uses skills, and wait- as well as having access to their ultimate skill."
    
    "\n\n=======\n\n"
    
    "There are a few battle types:\n"
    "1. Map/Main: The standard battle type.\n"
    "2. Wave Map/Main: Battles where the Player must face a set number of enemies. Losing once results in a failure\n"
    "3. Boss Map/ Main: The standard Boss battle type with little scaling."
    
    "\n\n=======\n\n"
    
    "4. Consecutive (Training): Like Wave battles, only with scaling and a 25% Health and Mana restore after each enemy.\n"
    "5. Timed (Training): Battles where the Player must defeat the Enemy within a set number of global actions.\n"
    "6. Cheater (Training): Battles where an Enemy is picked and rebuilt, adding/changing skills and ultimates from other enemies, while also changing their elemental affinities.\n"
    "7. Survival (Training): An indefinite form of scaled battles. Every 5 waves, a Boss Enemy will be fought and the scaling will be increased.\n"
    "8. Extreme (Training): Battle with a random map Boss.\n"
    f"9. Seasson (Training): A special type of batte with changing Theme. Fight four normal Enemies with the Theme active and then fight a Boss specific to that Theme. {Color['cyan']}Note: Go to 5. Themes for more{Color['reset']}.\n"
    "10. Gauntlet (Training): A series of battles of every Boss on the map."
)
guide_battle = Guide("Battle Info", guide_battle)

guide_meters = (
    "In battle, there are 3 meters that the Player should keep track of (besides Health and Mana):\n" 
    "Speed Meter: A meter that each battler has that has a threshold of 100 and carries overflow. Fills throughout the battle and allows a battler to act when full. Fills by a battlers Speed every tick. At higher Luck, there is a chance to recivie a 1-25 Speed Meter bonus every tick.\n"  
    "Ultimate Meter: A meter that only the Enemy has a threshold of 70 and carries overflow. Fills by 3 every tic and by the Enemies Speed / 4 every time global actions is a multiple of 5. When full, the Enemy will always use their ultimate skill.\n"  
    f"Sanity: A meter that each battler has that (normally) has a threshold of -25/25 and carries overflow when triggered. {Color['cyan']}Note: Go to 5. The Basics (Sanity) for more{Color['reset']}."  
    
    "\n\n=======\n\n"
    
    f"Some skills and statuses alter all 3 of these meters. {Color['cyan']}Note: Go to 7. Skills & 9. Statuses for more{Color['reset']}. "
)
guide_meters = Guide("Battle Meters", guide_meters)

guide_strikes = (
    "In battle their are many diffrent types of ways an attack or damaging skill can land on the opponent.\n"
    "These few are strikes only the Players damaging skills can land based on the Enemies elemenetal affinites:\n"
    f"Neutral ({symbols['Neutral']}): The Enemy will take damage normally.\n"
    f"Weak ({symbols['Weak']}): The Enemy will take increased damage (1.5x!). Gain/Lose sanity based on the skill used.\n"
    f"Super Weak ({symbols['Super Weak']}): The Enemy will take increased damage (2x!). Gain/Lose sanity based on the skill used.\n"
    f"Resist ({symbols['Resist']}): The Enemy will take decreased damage (0.5x!).\n"
    f"Null ({symbols['Null']}): The Enemy will not take any damage.\n"
    f"Reflect ({symbols['Reflect']}): The damage meant for the Enemy will be decreased (0.5x!) and dealt to the Player. Lose sanity always.\n"
    f"Absorb ({symbols['Absorb']}): The damage meant for the Enemy will be decreased (0.5x!) and be used to restore Health to the Enemy. Lose sanity always."

    "\n\n=======\n\n"
    
    "Onto the type of strikes that can be done by both Player and Enemy attacks and damaging skills:\n"
    f"Critical: Occurs when the users Luck + skills Critical stat is greater than a randomized number between 1-300. Increased damage (2x!). Gain/Lose sanity based on skill used.\n"
    f"{Color['yellow']}Super Critical{Color['reset']}: Buddy skill only. Same as a Critical, only the randomized number is between 1-400. Increased damage (2x!)."
    f"{Color['red']}Precision{Color['reset']}: Skill only. Occurs when half of the users Hit + skills Hit stat is greater than 100. Every point over 50 is taken as overflow. Increase damage (damage x (overflow x 0.2 / 100). Gain/Lose sanity based on skill used.\n"
    f"{Color['yellow']}Super{Color['red']} Precision{Color['reset']}: Skill only. Occurs when half of the users Hit + skills Hit stat is greater than 200. Every point over 175 is taken as overflow. Increase damage (damage x (overflow x 0.4 / 100). Gain/Lose sanity based on skill used.\n"
    f"{Color['cyan']}Buddy{Color['reset']}: Player Attack only. When a Buddy is equipped, there is a chance for the Buddy to deal additional damage after the Player uses attack."
    
)
guide_strikes = Guide("Strike Types", guide_strikes)

guide_sanity = (
    "In battles, it is best for the Player to keep an eye on their Sanity.\n"
    "By using skills, attacking, waiting, getting attacked, the Player gains/loses sanity. When reaching certain Sanity levels, certain things will happen:"
    
    "\n\n=======\n\n"
    
    "Positive Levels (Note: all Status inflictions can only happen if not already present):"
    "5 Sanity: If Sanity is at 5+, gain Boost I and (passively) restore Mana/Health (Player / Enemy) (Sanity / 2).\n"
    "10 Sanity: If Sanity is at 10+, gain Tough I and (passively) theres a chance to remove up to 2 Negative statuses.\n"
    "15 Sanity: If Sanity is at 15+, gain Boost II.\n"
    "20 Sanity: If Sanity is at 20+, gain Tough II.\n"
    "25+ Sanity: If Sanity is at 25+, gain Tranquil/Boost III (Player / Enemy) and lose 25 Sanity (keep any overflow Positive Sanity)."

    "\n\n=======\n\n"
    
    "Negative Levels (Note: all Status inflictions can only happen if not already present):"
    "-5 Sanity: If Sanity is below -5, gain Clouded I and (passively) lower Speed Meter by 5-15.\n"
    "-10 Sanity: If Sanity is below -10, gain Consumed and (passively) theres a chance to extend the duration of up to 2 Negative statuses by 1.\n"
    "-15 Sanity: If Sanity is below -15, gain Clouded II.\n"
    "-20 Sanity: If Sanity is below -20, gain Sinking.\n"
    "-25+ Sanity: If Sanity is below -25+, gain 2 stacks of Sinking and gain 25 sanity (keep overflow Negative Sanity)."
    
    "\n\n=======\n\n"
    
    f"Some skills alter Sanity levels of the user or opposer, others require Sanity to activate certain effects. {Color['cyan']}Note: Go to 9. Classes for more{Color['reset']}."
)
guide_sanity = Guide("The Basics (Sanity)", guide_sanity)

guide_themes = (
    "Themese are a passive effect certain battles will have. The occur to both battlers after having acted.\n"
    "Here are 4 basic examples of Themes:\n"
    
    f"1.  {Color['red']}Summer{Color['reset']}: After acting, gain Burn/Heated(if Burn is at max stacks). Fire skills have a chance to inflict Sear on either the user or opposer.\n"
    f"2. {Color['blue']}Winter{Color['reset']}: After acting, there is a small chance to gain Deep Freeze. If any Chill statuses are present, chance to gain Frai II/Cripple I. Ice skills always inflict Freeze.\n"
    f"3. {Color['yellow']}Fall{Color['reset']}: After acting, gain either of; Shock, Overload, or Static. Based on the number of Shock statuses present, gain Boost I/Boost II/Boost III. Thunder skills always inflict Static.\n"
    f"4. {Color['magenta']}Spring{Color['reset']}: After acting; gain 1 Poison or Bleed status, Poison statuses count (turns active) increase by 2, and chance to retrigger Bleed/Poison statuses. Wind skills have a chance to inflict a Bleed status on the opposer.\n"
    
    "Each of these Themes occur for both battlers. Think of them as a global passive that is sometimes benificial to the Player, or the Enemy.\n"
)
guide_themes = Guide("Themes", guide_themes)

guide_skills = (
    f"In Ruin Fountain, skills are the backbone of a Players build (as well as sigils). {Color['cyan']}Note: Go to 8. Equipables for more{Color['reset']}.\n"
    "These are the shared attributes by most skills:\n"
    "Cost: Player only. The amount of Mana required to use a skill. Each skill has a base Mana cost, the actual cost is the base cost + 6% of the Players Mana.\n"
    "Cooldown: Player only. The amount of actions needed before it's usable."
    
    "\n\n=======\n\n"
    
    "There are 5 types of skills:\n"
    f"{Color['red']}Damaging{Color['reset']} Skills: These skills deal damage using the users stats versus the opposers stats (usally Strength vs. Defense or Magic vs. Resistance). These skills have an element, Hit stat, and Critical stat. These skills can also inflict statuses on the opposer/user.\n"
    f"{Color['red']}Mutli Hit{Color['reset']} (Sub): Damaging skills that deal damage multiple times. Every hit after another deals 30% of the previous hits damage.\n"
    f"{Color['yellow']}Healing{Color['reset']} Skills: These skills restore Health/Mana. They sometimes inflict Positive statuse on the user.\n"
    f"Status Skills: These skills inflict statuses on the opposer/user. Sometimes the statuses inflicted by these skills are conditional.\n"
    f"{Color['cyan']}Special{Color['reset']} Skills: These skills are purely unique in effect. They don't fit in with the others.\n"
    f"{Color['magenta']}Passive{Color['reset']} Skills: These cannot be used and have no cost or cooldown. After acting, these skills will check if they can activate, and if so, there effect will go through. Some of these skills have conditional requirements for their effects to happen."
    
    "\n\n=======\n\n"
    
    "Skill Example 1#:\n"
    f"{Color['yellow']}Blizga | Cost: 9 | Cooldown: 3 | Ice | Positive{Color['reset']}\n"
    f"{Color['yellow']}Magic vs. Resistance x 2. Chance to inflict Deep Freeze/Absolute Zero.{Color['reset']}\n"
    f"{Color['yellow']}Hit: 70 | Critical: 30{Color['reset']}\n\n"
    
    "The damaging skill Blizga is shown as Example #1. As read, the skill uses the Players Magic and targets the Enemies Resistance. It also hits 2 times.\n"
    "The skill also has a chance to inflict 2 statuses- Deep Freeze and Absoulte Zero- which will be indivisually be rolled for infliction."
    "At it's core though, Blizga is an Ice element skill with a base cost of 9 and a cooldown of 3. The skills Hit is 70 and it's Critical is 30."
    "Most importantly though, the skill is a Positive leaning skill. This means that any sanity gained from landing a beneficial strike (Critical, Precision, etc.) will be Positive (+1, +10).\n"
    "A skill that is Negative leaning would give the user Negative sanity on beneficial strikes (-1, -10).\n\n"
    
    "Skill Example 2#:\n"
   f"{Color['yellow']}Cure | Cost: 8 | Cooldown: 4 | None {Color['reset']}\n"
    f"{Color['yellow']}Restore health (10% of Max Health + 50% of Magic). Increased healing (5% of Max Health) if any Negative statuses are removed on use. Chance to remove 1 Negative status.{Color['reset']}\n"
    f"{Color['yellow']}Hit: 0 | Critical: 0{Color['reset']}\n\n"
    
    "The healing skill Cure is shown as Example 2#. As read, the skill restores Health to the Player based on their Max Health + their Magic.\n"
    "The skill also has two effect; 1. There is a chance to remove 1 Negative status, and 2. Increase the amount healed by 5% of Max Health if any Negative statuses are removed.\n"
    "You may notice that Cure has no Sanity leaning. This is beacuse all healing skills give Sanity, no matter what. Healing skills also have no Hit or Critical, they have no use for them.\n"
    "They do have a base cost and cooldown.\n\n"
    
    
    "Skill Example 3#:\n"
    f"{Color['yellow']}Double Up{Color['reset']}\n"
    f"{Color['yellow']}If Wait is used, for each Negative status that stacks present on the opposer, at a chance of 5% + 5% per 10 points of Luck (max 60%), inflict 1 stack of the status (with 2 count (if applicable)).{Color['reset']}\n\n"
    
    "Passives are unique amoung skills. They cannot be used like other skills (thus having no cost, cooldown, Hit, Critical, element, etc.), but they have very special effects.\n"
    "Example 3#, aka Double Up, requires the Player to use the wait action for its effect to take place, while also needing the Enemy to have any Negative statuses present.\n"
    "This type of passive would be good for a status heavy build!"
    
    "\n\n=======\n\n"
    
    "Every skill type can have conditionals for certain effects. Keep an eye on what the conditionals the skills you have equiped require!\n"
    f"{Color['cyan']}Note: Go to 8. Equipables & 9. Statuses for more.{Color['reset']}"
)
guide_skills = Guide("Skills", guide_skills)

guide_equips = (
    "In Ruin Fountain, the Player has access to skills and sigils- plus another equip type. {Color['cyan']}Note: Go to 1. Buddies for more{Color['reset']}..\n"
    f"Skills are equipables that allow the Player to do a variety of things and that usually need to be activated. {Color['cyan']}Note: Go to 7. Skills for more{Color['reset']}.\n"
    "Sigils are equipables that (most of the time) alter the Players stats and that have passive effects that grant the Player a leg up in battle."
    "Both can be found across Ruin Fountain, either via buying them or being rewarded with them."
    
    "\n\n=======\n\n"
        
    "Sigil can be 1 of 3 affinities:\n"
    "1. Power: The offensive and Physical focused sigils.\n"
    "2. Survival: The sigils focused on defense and sustain.\n"
    "3. Utility: The Magic and conditional focused sigils."
    
    "\n\n=======\n\n"
    
    "Example Sigil: \n"
    f"{Color['yellow']}1. Warmth Sigil | 2. Emits a campfire like aura.{Color['reset']}\n"
    f"{Color['yellow']}3. Utility | 4. Raise Speed by 5. Restores health (4% of Max Health + 1-3) each action.{Color['reset']}\n\n"

    "As shown above, this sigils is split into 4 sections of note- Name, Flavor Text, Affinity, and Effect.\n"
    "As read, the Warmth Sigil would raise the Players Speed by 5 (these stat increases carry over out of battle but are removed once the sigil is unquipped) and after the Player acts, they would heal.\n\n"
    
    f"{Color['yellow']}If a sigil raises Max Mana, the cost of your skills will stay the same!{Color['reset']}"
    "\n\n=======\n\n"
    
    f"{Color['yellow']}The Player can equip up to 6 skills, up to 3 sigils, and 1 buddy!{Color['reset']}. {Color['cyan']}Note: Go to 10. Skills for more{Color['reset']}."
)
guide_equips = Guide("Equipables", guide_equips)

guide_statuses = (
    "There a 7 families of statuses:\n"
    f"{Color['yellow']}Burn{Color['reset']}: These statuses are usually inflicted via Fire element skills. This is a damage focused Status family that has little stat debuffing.\n"
    f"{Color['red']}Bleed{Color['reset']}: These statuses are usually inflicted via Physical element skills. This is a damage and status synergy focused family. At it's best when there are multiple statuses of the same family.\n"
    f"{Color['green']}Poison{Color['reset']}: This family focuses on persisting and lingering to deal more damage. All statuses of this family have an attribute called count (turns active). It can grow indefinitely.\n"
    f"{Color['blue']}Chill{Color['reset']}: These statuses are usually inflicted via Ice element skills. This family is focused on debuffing and slowing down momentum.\n"
    f"{Color['yellow']}Shock{Color['reset']}: These statuses are usually inflicted via Thunder element skills. Unlike the other families, this family is about stacking statuses and buffing. Mose statuses of this family are Positive.\n"
    f"{Color['magenta']}Mental{Color['reset']}: This family is a varying cascade. Buffs, debuffs, damage, etc. But 1 thing is shared by all statuses (or most), they all alter sanity- whether Positive or Negative. {Color['cyan']}Note: Go to 5. Sanity for more.{Color['reset']}\n"
    f"Other: Everything else. Buffs, debuffs, damage, damage increases, damage decreasers, everything else!\n"
    f"Info: {Color['yellow']}Some Statuses restricts a battler from acting for 1 or more actions (Stun, Burnout, Deep Freeze, etc.). Watch out for them!{Color['reset']}\n"
    "Statuses that share a family are grouped together. Skills, sigils, and other statuses can search for them."
    
    "\n\n=======\n\n"
    
    "Statuses can be 1 of 3 alignments:\n"
    "Positive: A status that is a boon to the afflicted.\n"
    "Negative: A status that hinders the afflicted.\n"
    "Neutral: A status that exist.\n"
    "Like status families, the alignment of a Status links groups them with others- though less tightly."
    
    "\n\n=======\n\n"
    
    "Status Example 1# (Battle Screen):\n"
    f"{Color['yellow']}Health: XXX/XXX | Sanity: X{Color['reset']}\n"
    f"{Color['yellow']}Strength: XX | Magic: XX{Color['reset']}\n"
    f"{Color['yellow']}Defense: XX | Resistance: XX{Color['reset']}\n"
    f"{Color['yellow']}Luck: XXX | Hit: XXX | Speed: XX{Color['reset']}\n"
    f"{Color['yellow']}Statuses: {Color['red']}Burn (1/3) [1/5]{Color['reset']}, {Color['red']}Volcanic (0/2){Color['reset']}\n\n"
    
    "In Example 1# the battler is shown to be inflicted with Burn and Volcanic, 2 Burn statuses.\n"
    "The numbers on the side of the Status names are the duration (1/3, 0/2). The duration of a Status rises every time the afflicted acts and until it reaches its max duration.\n"
    "Next to Burn's duration is it's stack amount (it has 1 stack and has a max stack of 5). The stack of a Status is important beacuse it makes the effects of the Status more potent.\n"
    "This is what you can expect to see during battles.\n\n"
    
    "Status Example 2# (Analyze):\n"
    f"{Color['yellow']}Poison | Duration: 1/5 | Stacks: N/A | Count: 1{Color['reset']}\n"
    f"{Color['yellow']}Deals damage (3% of Max Health + 1-3 + count (turns active) x 2). Last 5 actions.{Color['reset']}\n\n"
    
    "In Example 2# the battler is looking at the analyze screen to get more information about the Poison status, which is a Status in the Poison family Status.\n"
    "As shown, Poison looks like it's just been inflicted. It also can't stack. But look to the right of that and you see count.\n"
    "Some skills have a count attribute that is only viewable in the analyze screen. Not all statuses use count in the same way.\n"
    "This is what you can expect in the analyze screen."
    
    "\n\n=======\n\n"
    
    "Few things to note about statuses:\n"
    "1. Some statuses can stack. Stacking usually increases a statuses effects- whether good or bad.\n"
    "2. Some statuses will remove other statuses. 1 will remove the other.\n"
    "3. Some statuses can last forever. Not all of them have a set duration."
    
    "\n\n=======\n\n"
    
    "Statuses have many effects. Damage dealers, healing, group checkers, and much more.\n"
    f"{Color['yellow']}They are one aspect to keep in mind when playing!{Color['reset']}"
)
guide_statuses = Guide("Statuses", guide_statuses)

guide_buddies = (
    f"Buddies are a unique type of equimpment that the Player has access too starting at level 5 (From the Buddy Shop in Training Halls). Only 1 can be equipped at a time.\n"
    f"Buddies have their own stats:\n"
    "Attack: For a Buddies damaging or healing skills.\n"
    "Talent: If a Buddies damaging skill lands or if a critical lands or status is inflicted.\n"
    "Speed: The Buddies stats.\n"
    
    "Buddies can level up to level 10! Starting at level 0, they need 100 EXP and then another 200 for each level!\n"
    "You can get items from the Buddy Care Shop in the Start Zone that give your Buddy EXP!\n"
    "On level up, a Buddies Attack will be increased by 3 and Talent will be increased by 2, but their Speed will remain the same!\n"
    
    "Certain items can be used to increase a Buddy's Attack, Talent, or Speed!\n"
    "Do keep in mind, a Buddy can only use 6 of these items, and once the cap is reached, they will refuse any other these items!\n"
    "You can get these items from the Buddy Care Shop in the Start Zone!\n"
    
    "The Buddy Care Shop becomes available from level 5 onward!"
    
    "\n\n=======\n\n"
    
    "The Players Buddy has a Buddy Meter. Once full, the Buddy will use their skill. The Buddies passive always is always active.\n"
    "The Buddy Meter is raised by a quarter of the Players Speed + the Buddies Speed. It has to reach 120 for the Buddy to use its skill."
    
    "\n\n=======\n\n"
    
    "Each Buddy has a passive and an active skill.\n"
    "The Buddies passive will always run after the Players passives and their skill will only run once the Buddy Meter is full.\n"
    f"If the Player uses attack and has a Buddy equipped, there is a chance that a Buddy Strike will happen. {Color['cyan']}Note: Go to 4. Strikes for more.{Color['reset']}\n"
    "Also, damaging Buddy skills use this formula: (Attack - (opposers Defensive stat / 6) x 5) x multiplier. Buddies use a 6:5 ratio!"
)
guide_buddies = Guide("Buddies", guide_buddies)

guide_item_storage = (
    "When wanting to store more items of the same type, you can put them in your item storage.\n"
    "Keep in mind, there won't be storage tiles on each map!"
)
guide_item_storage = Guide("Item Storage", guide_item_storage)

guide_raids = (
    "After reaching level 15, your very first Raid will become available.\n"
    "Raids are challenges that requrie put together builds, including skills, sigils, buddies, and stat modifiers.\n"
    "Don't worry about items, as they are removed while in a Raid."

    "\n\n=======\n\n"

    "When entering a Raid, the Player's base Speed is capped at 30 and base Strength, Magic, Defense, and Resistance are reduced by 25%!\n"
    "The Player is then made to battle through 5 randomly picked maps. On map 1-3, an enemy is chosen from a pool of enemis you won't find anywhere else. Each of these enemies will be given a random theme and passive from a pool.\n"
    "Map 4 is the Raid Boss's lacky. These enemies share quirks with the Raid Boss!\n"
    "Finally, on Map 5, is the Raid Boss!"

    "\n\n=======\n\n"
    
)
guide_raids = Guide("Raids", guide_raids)
