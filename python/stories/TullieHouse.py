from milecastles import Story, Box, ThroughPage, ThroughSequence, ConditionFork, NodeFork, SackChange
from stories import introText

# inspects the module to figure out the story name (e.g. corbridge)
storyName = "TullieHouse"

# create story
story = Story(
    uid=storyName,
    version="0.1.0",
    startNodeUid="firstLanding",
    startSack={
            "money":  100,
            "horse": 0,
            "sword":  0,
            "trojan":  False,
            "arstech":  False,
            "amazon":  False,
            "archery":  0,
            "victory": 0,
    }
)

with story:

    # populate with boxes

    fortBox =         Box( uid="1",   label="Box I",      description="the Fort")
    gateBox =       Box( uid="2",   label="Box II",     description="the Arena Gates")
    arenaBox =           Box( uid="3",   label="Box III",    description="the Arena")
    garrisonBox =         Box( uid="4",   label="Box IV",     description="the Garrison")

    entranceBox = fortBox

	#Intro
    ThroughPage(
        uid="firstLanding",
        goalBoxUid=entranceBox.uid,
        page=introText,
        nextNodeUid="landing",
        )

    ThroughSequence(
		uid =           "landing",
		change =        SackChange(
							reset=story.startSack
							),
		goalBoxUid =    fortBox.uid,
		nextNodeUid =   "mask1",
		sequence = [
            """ You are Grecus
				Turmaerious, a member
				of the Super Turma
				Cavalry Troop,
				Favoured by the God
				Epona!
				...""",
            """ Your quest is to show
				off your riding and
				weapon skills in front
				of the crowd at the
                Hippika Gymnasia games
                at Fort Uxelodunum...""",
			""" Go over to the fort
				entrance at BOX II
				to start your quest!""",
        ],
    )
				#23456789012345678901234

    ThroughSequence(
		uid =           "mask1",
		change =        SackChange(
							reset=story.startSack
							),
		goalBoxUid =    gateBox.uid,
		nextNodeUid =   "maskFork1",
		sequence = [
            """ You are at the entrance
				to the games arena.
				Before entering, you
				need to choose your
				mask...""",
            """ Will you be a TROJAN
				with a focus on
				teamwork and sword
				skills?
				...""",
            """ Or an AMAZON, with a
				focus on archery
				and horse riding
				skills?
				...""",
        ],
    )
								#23456789012345678901234
					#Amazon / Trojan mask selection
    NodeFork(
        uid =   "maskFork1",
        choices = {
			"trojan1":    	""" Collect the TROJAN mask
								at the fort""",
            "amazon1":   	""" Collect the AMAZON mask
								at the garrison""",
				}
			)
							#23456789012345678901234
    ThroughPage(
		uid="trojan1",
		page=			""" You search the armoury
							at the fort and find a
							TROJAN mask!
							TAKE A SELFIE wearing a
							helmet in the SELFIE
							AREA then come back...""",
		goalBoxUid = fortBox.uid,
		nextNodeUid="trojan2",
    )
							#23456789012345678901234
    ThroughPage(
		uid="trojan2",
		change =        SackChange(
							assign={"trojan":True},
							plus={"sword":10}
							),
		page=			""" Your sword skill went
							up by {{node.change.plus['sword']}}!
							Now return to your Turma
							at the arena gates.""",
		goalBoxUid = fortBox.uid,
		nextNodeUid="gate1",
    )
							#23456789012345678901234
    ThroughPage(
		uid="amazon1",
		page=			""" You search the garrison
							and find an AMAZON mask!
							TAKE A SELFIE wearing a
							helmet in the SELFIE
							AREA then come back...""",
		goalBoxUid = garrisonBox.uid,
		nextNodeUid="amazon2",
    )
							#23456789012345678901234
    ThroughPage(
		uid="amazon2",
		change =        SackChange(
							assign={"amazon":True},
							plus={"archery":10}
							),
		page=			""" Your archery skill went
							up by {{node.change.plus['archery']}}!
							Now return to your Turma
							at the arena gates.""",
		goalBoxUid = garrisonBox.uid,
		nextNodeUid="gate1",
    )
		# First training Fork
				#23456789012345678901234

    ThroughSequence(
		uid =           "gate1",
		goalBoxUid =    gateBox.uid,
		nextNodeUid =   "trainingFork1",
		sequence = [
            """ You return to the
				gates and meet with
				members of your Turma,
				Festus and Docca. They
				are talking about a
				strategy tablet called
				the 'Ars Technica'...""",
            """ You think about going
				to collect it from
				Victor, a groom visiting
				from Arbeia, but you
				still need to prepare
				for the games...""",
            """ Festus says:
				'You only have one hour
				do so much before the
				games begin! Did you
				make an offering to
				epona yet?'
				...""",
        ],
    )

    NodeFork(
        uid =   "trainingFork1",
        choices = {
			"arsTech1":    	""" Collect the Ars Technica
								at the fort """,
          	"weapon1":   	""" Train with your weapon
								at the arena.""",
			  "epona1":   	""" Make an offering to
								Epona""",
				},
								 hideChoices={
            "arstech1": "sack.arstech==True",
				}
			)
							#23456789012345678901234
    ThroughPage(
		uid="arsTech1",
		change =        SackChange(
							assign={"arstech":True},
							),
        page=			""" You track down Victor
							and he lets you read
							the 'Ars Technica'
							INVESTIGATE the displays
							for info on tactics,
							then come back...""",
		goalBoxUid = fortBox.uid,
		nextNodeUid="rest1",
    )
							#23456789012345678901234
    ThroughPage(
		uid="epona1",
		change =        SackChange(
							plus={"horse":10},
							),
        page=			""" You return to the
							garrison and find an
							altar. MAKE AN OFFERING
							of wine to Epona to
							increase your horse
							skills by {{node.change.plus['horse']}}...""",
		goalBoxUid = garrisonBox.uid,
		nextNodeUid="rest1",
    )
						#check for sword / archery
    ConditionFork(
        uid=           "weapon1",
        condition =    "sack.archery >= 10",
        trueNodeUid=   "archery1",
        falseNodeUid=  "sword1",
    )

							#23456789012345678901234
    ThroughPage(
		uid="archery1",
		change =        SackChange(
							plus={"archery":10},
							),
        page=			""" The arena is quiet
							before the games.
							You take time to
							PRACTICE YOUR ARCHERY,
							raising your skllls
							by {{node.change.plus['archery']}}...""",
		goalBoxUid = arenaBox.uid,
		nextNodeUid="rest1",
    )
							#23456789012345678901234
    ThroughPage(
		uid="sword1",
		change =        SackChange(
							plus={"sword":10},
							),
		page=			""" The arena is quiet
							before the games.
							You take time to
							PRACTICE with your
							SWORD, raising
							your skllls by {{node.change.plus['sword']}}...""",
		goalBoxUid = arenaBox.uid,
		nextNodeUid="rest1",
    )
				#23456789012345678901234
    ThroughSequence(
		uid =           "rest1",
		goalBoxUid =    garrisonBox.uid,
		nextNodeUid =   "trainingFork2",
		sequence = [
            """ You take a short
				rest after your
				training.
				You are excited
				about the games...""",
            """ Do you want to
				train some more?
				...
				""",
        ],
    )
				#Second training Fork (optional) Ars Tech not available in second fork

    NodeFork(
        uid =   "trainingFork2",
        choices = {
			"trainingYes":	""" Yes! More I want to
								train more """,
            "rest2":   		""" No! I'll go straight
								to the games """,
				}
			)

    ThroughPage(
		uid="trainingYes",
		page=			""" What kind of
							training?""",
		goalBoxUid = arenaBox.uid,
		nextNodeUid="trainingFork3",
    )

    NodeFork(
        uid =   "trainingFork3",
        choices = {
			"epona2":   	""" Make an offering to
								Epona""",
			"weapon2":   	""" Train with your weapon
								at the arena.""",
				},
			)

    ThroughPage(
		uid="epona2",
		change =        SackChange(
							plus={"horse":10},
							),
        page=			""" You return to the
							garrison and find an
							altar. MAKE AN OFFERING
							of wine to Epona to
							increase your horse
							skills by {{node.change.plus['horse']}}...""",
		goalBoxUid = garrisonBox.uid,
		nextNodeUid="rest2",
    )

    ThroughPage(
		uid="weapon2",
		page=			""" You take some time
							to choose a better
							weapon back at the
							fort. Now head to
							the arena.""",
		goalBoxUid = fortBox.uid,
		nextNodeUid="weapon3",
    )

    ConditionFork(
        uid=           "weapon3",
        condition =    "sack.archery >= 10",
        trueNodeUid=   "archery2",
        falseNodeUid=  "sword2",
    )

							#23456789012345678901234
    ThroughPage(
		uid="archery2",
		change =        SackChange(
							plus={"archery":10},
							),
        page=			""" The arena is quiet
							before the games.
							You take time to
							PRACTICE YOUR ARCHERY,
							raising your skllls
							by {{node.change.plus['archery']}}...""",
		goalBoxUid = arenaBox.uid,
		nextNodeUid="rest2",
    )
							#23456789012345678901234
    ThroughPage(
		uid="sword2",
		change =        SackChange(
							plus={"sword":10},
							),
		page=			""" The arena is quiet
							before the games.
							You take time to
							PRACTICE with your
							SWORD, raising
							your skllls by {{node.change.plus['sword']}}...""",
		goalBoxUid = arenaBox.uid,
		nextNodeUid="rest2",
    )

    # Rest / Epona check

    ThroughPage(
        uid =           "rest2",
        goalBoxUid =    fortBox.uid,
        change = SackChange(
            trigger = "sack.horse <= 9",
            plus  =     {"horse":20},
        ),
        page = """
            {% if node.change.triggered %}
                {% if node.change.completed %}
                    Your horse is tired
                    and pale... you make
                    an offering to the
                    horse god Epona raising
                    your horse skills by {{node.change.plus['horse']}},
           {% else %}
					Your horse is looking
					healthy, thanks to
					Epona! Festus & Docca
					mock you for trusting
					in a Celtic god!
					{% endif %}
            {% else %}
					Your horse is looking
					healthy, thanks to
					Epona! Festus & Docca
					mock you for trusting
					in a Celtic god!
            {% endif %}
        """,
        nextNodeUid = "gate2",
    )


    ThroughPage(
		uid="gate2",
		missTemplate =  """ This isn't the arena!
							Go to {{node.goalBox.label}}""",
        page=			""" The games have begun,
							and the crowd roars
							from inside the arena.
							You join the rest of
							your turma outside.""",
		goalBoxUid = gateBox.uid,
		nextNodeUid="gamesFork1",
    )

    #Fork to detect arstech / add victory points

    ConditionFork(
        uid=           "gamesFork1",
        condition =    "sack.arstech == True",
        trueNodeUid=   "plan1",
        falseNodeUid=  "noPlan1",
    )
							#23456789012345678901234

    ThroughPage(
		uid="plan1",
        page=			""" You tell Festus & Docca
							about your new tactics
							and make a plan with the
							rest of the turma...""",
		goalBoxUid = gateBox.uid,
		nextNodeUid="turma1",
    )

    ThroughPage(
		uid="turma1",
		change =        SackChange(
							plus={"victory":1},
							),
        page=			""" You perform a show-
							stopping display of
							tactics! The crowd goes
							wild! You've earned
							{{node.change.plus['victory']}} laurel wreath...""",
		goalBoxUid = arenaBox.uid,
		nextNodeUid="gatePrep1",
    )
							#23456789012345678901234

    ThroughPage(
		uid="noPlan1",
        page=			""" You don't really have
							much of a plan for the
							tactics display, but
							Festus has bought a
							roast pig to share -
							YUM!""",
		goalBoxUid = gateBox.uid,
		nextNodeUid="noPlan2",
    )

    ThroughPage(
		uid="noPlan2",
        page=			""" Ouch! Now everyone has
							indigestion and the
							display is a bit of a
							mess. Not totally bad,
							just a bit average...""",
		goalBoxUid = arenaBox.uid,
		nextNodeUid="gatePrep1",
    )

    ThroughPage(
		uid="gatePrep1",
        page=			""" Next, you grab
							your weapon and
							prepare to show
							off your skills
							...""",
		goalBoxUid = gateBox.uid,
		nextNodeUid="gamesFork2",
    )

    #weapons fork - test for sword or archery

    ConditionFork(
        uid=           "gamesFork2",
        condition =    "sack.archery >= 10",
        trueNodeUid=   "arrowTarget1",
        falseNodeUid=  "swordTarget1",
    )
	#arrow test
							#23456789012345678901234
    ThroughPage(
		uid="arrowTarget1",
        page=			""" You carefully line up
							your arrow... the crowd
							holds it's breath...""",
		goalBoxUid = arenaBox.uid,
		nextNodeUid="arrowFork1",
    )

    ConditionFork(
        uid=           "arrowFork1",
        condition =    "sack.archery >= 20",
        trueNodeUid=   "arrowSuccess",
        falseNodeUid=  "arrowFail",
    )

    ThroughPage(
		uid="arrowSuccess",
		change =        SackChange(
							plus={"victory":1},
							),
        page=			""" You let the arrow fly
							and get a BULLSEYE!
							The crowd loves you!
							You've earned
							{{node.change.plus['victory']}} laurel wreath
							...""",
		goalBoxUid = arenaBox.uid,
		nextNodeUid="horseGate",
    )

    ThroughPage(
		uid="arrowFail",
        page=			""" You let the arrow fly
							and... the wind catches
							it, sending it to the
							edge of the target.
							The crowd boos...""",
		goalBoxUid = arenaBox.uid,
		nextNodeUid="horseGate",
    )

    #sword test
							#23456789012345678901234
    ThroughPage(
		uid="swordTarget1",
        page=			""" You draw your sword and
							galop towards the target
							dummy...
							the crowd murmurs...""",
		goalBoxUid = arenaBox.uid,
		nextNodeUid="swordFork1",
    )

    ConditionFork(
        uid=           "swordFork1",
        condition =    "sack.sword >= 20",
        trueNodeUid=   "swordSuccess",
        falseNodeUid=  "swordFail",
    )
							#23456789012345678901234

    ThroughPage(
		uid="swordSuccess",
		change =        SackChange(
							plus={"victory":1},
							),
        page=			""" You wield your sword
							with gusto and send
							the dummy crashing to
							the ground!
							You've earned
							{{node.change.plus['victory']}} laurel wreath
							...""",
		goalBoxUid = arenaBox.uid,
		nextNodeUid="horseGate",
    )

    ThroughPage(
		uid="swordFail",
        page=			""" You slash wildly with
							your sword, but the
							dummy only wobbles...
							the crowd giggles...""",
		goalBoxUid = arenaBox.uid,
		nextNodeUid="horseGate",
    )

    #horsetest
							#23456789012345678901234
    ThroughPage(
		uid="horseGate",
        page=			""" You take a short rest
							before the final round
							of the games...
							You make a prayer to
							Epona...""",
		goalBoxUid = gateBox.uid,
		nextNodeUid="horseFork1",
    )

    ConditionFork(
        uid=           "horseFork1",
        condition =    "sack.horse >= 20",
        trueNodeUid=   "horseWin1",
        falseNodeUid=  "horseFail1",
    )
							#23456789012345678901234

    ThroughPage(
		uid="horseWin1",
       change =        SackChange(
							plus={"victory":1},
							),
        page=			""" You ride your horse
							around the obstacle
							course like an expert!
							The crowd chants your
							name! You've earned
							{{node.change.plus['victory']}} laurel wreath...""",
		goalBoxUid = arenaBox.uid,
		nextNodeUid="endFork1",
    )

    ThroughPage(
		uid="horseFail1",
        page=			""" Your riding skills are
							less than great...
							You wobble all over
							the place and the
							crowd throw rotten
							vegetables...""",
		goalBoxUid = arenaBox.uid,
		nextNodeUid="endFork1",
    )

    ConditionFork(
        uid=           "endFork1",
        condition =    "sack.victory == 3",
        trueNodeUid=   "goodEnd1",
        falseNodeUid=  "badEnd1",
    )


    # end of games - use win points to give good / bad ending
				#23456789012345678901234

    ThroughSequence(
		uid =           "goodEnd1",
		goalBoxUid =    gateBox.uid,
		nextNodeUid =   "landing",
		sequence = [
            """ You feel GREAT!
				You won in every round
				of the games!
				...""",
            """ You celebrate with your
				Turma, knowing that
				people will talk about
				your peformance for
				years to come...""",
			"""	You won the games with:
                {% if sack.arstech == True %}
                    A genuine Ars Technica!
                {% else %}
                    No Ars Technica. Shame.
                {% endif %}
				Horse Skill: {{sack.horse}}.
				Sword Skill: {{sack.sword}}.
				Archery Skill: {{sack.archery}}""",
            """ Go back to BOX 1
				to play again or
				visit another museum
				to play more
				Milecastles!
				""",
        ],
    )
				#23456789012345678901234

    ThroughSequence(
		uid =           "badEnd1",
		goalBoxUid =    gateBox.uid,
		nextNodeUid =   "landing",
		sequence = [
            """ Your break in formation
				and lack of training
				led to a very average
				display...""",
            """ It's a sad day for your
                Turma but there's always
				next year!
				...""",
			"""	You ended the games with:
                {% if sack.arstech == True %}
                    A genuine Ars Technica!
                {% else %}
                    No Ars Technica. Shame.
                {% endif %}
                Horse Skill: {{sack.horse}}.
				Sword Skill: {{sack.sword}}.
				Archery skill: {{sack.archery}}""",
            """ Go back to BOX I
				to try again or
				visit another museum
				to play more
				Milecastles!
				""",
        ],
    )

def run():
    from regimes.console import ConsoleSiteEmulator
    emulator = ConsoleSiteEmulator(story=story)
    emulator.run()

if __name__ == "__main__":
    run()