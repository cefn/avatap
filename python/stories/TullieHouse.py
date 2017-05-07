from milecastles import Story, Box, ThroughPage, ThroughSequence, ConditionFork, NodeFork, SackChange
from engines.console import ConsoleSiteEmulator
# inspects the module to figure out the story name (e.g. corbridge)
storyName = __name__.split(".")[-1]

# create story
story = Story(
    uid=storyName,
    startNodeUid = "landing",
    startSack={
            "money":  100,
            "horse": 10,
            "sword":  10,
            "trojan":  False,
            "arstech":  False,
            "amazon":  False,
            "archery":  10,
    }
)

with story:

    # populate with boxes

    fortBox =         Box( uid="1",   label="Box I",      description="the Fort")
    gateBox =       Box( uid="2",   label="Box II",     description="the Arena Gates")
    arenaBox =           Box( uid="3",   label="Box III",    description="the Arena")
    garrisonBox =         Box( uid="4",   label="Box IV",     description="the Garrison")

    entranceBox = fortBox

	#count     123456789x123456789x123456

	#1. Intro / Prep

    ThroughSequence(
		uid =           "landing",
		change =        SackChange(
							reset=story.startSack
							),
		goalBoxUid =    fortBox.uid,
		nextNodeUid =   "mask1",
		sequence = [
            """ Welcome to Milecastles!
				Look for numbered boxes
				and tap your card to
				progress the story!""",
            """ You are Grecus
				Turmaerious, a member of
				the glorious Super Turma
				Cavalry Troop!""",
            """ Skilled on horseback and
				favoured by the God of
				Epona, you could say that
				you're a super trooper!""",
            """ Your quest is to show
				off your riding, archery
				and sword skills at the
                Hippika Gymnasia games
                at Uxelodunum fort.""",
			""" Go over to the fort
				entrance to start your
				quest!""",
        ],
    )
	#count     123456789x123456789x123456

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
				Before entering, you need
				to choose your team.
				Will you be:""",
            """ A Trojan with a
				focus on team work
				and sword skills?
				or...""",
            """ ...an Amazon, with
				a focus on archery
				and horse riding
				skills?""",
        ],
    )

    NodeFork(
        uid =   "maskFork1",
        choices = {
			"trojan1": """
            Collect the Trojan
            mask from the fort.
            """,
            "amazon1": """
            Collect the Amazon
            mask from the garrison.
            """,
            }
        )

	#2 Amazon / Trojan selection
				#count     123456789x123456789x123456

    ThroughPage(
		uid="trojan1",
		missTemplate =  """ This isn't the {{node.goalBox.description}}!
							Go to {{node.goalBox.label}}""",
        page=			""" You search the armoury
							at the fort and find a
							Trojan mask.
							TAKE A SELFIE wearing a
							helmet in the SELFIE
							AREA!""",
		goalBoxUid = fortBox.uid,
		nextNodeUid="trojan2",
    )

    ThroughPage(
		uid="trojan2",
		change =        SackChange(
							assign={"trojan":True},
							plus={"sword":10}
							),
		missTemplate =  """ This isn't the {{node.goalBox.description}}!
							Go to {{node.goalBox.label}}""",
        page=			""" You chose Trojan!
							Your sword skills went up
							by {{node.change.plus['sword']}}!
							Now return to your Turma at
							the arena gates.""",
		goalBoxUid = fortBox.uid,
		nextNodeUid="gate1",
    )

    #3 amazon section
				#count     123456789x123456789x123456

    ThroughPage(
		uid="amazon1",
		missTemplate =  """ This isn't the garrison!
							Go to {{node.goalBox.label}}""",
        page=			""" You search the garrison
							and find the Amazon mask.
							TAKE A SELFIE wearing a
							helmet in the
                            SELFIE AREA!""",
		goalBoxUid = garrisonBox.uid,
		nextNodeUid="amazon2",
    )

    ThroughPage(
		uid="amazon2",
		change =        SackChange(
							assign={"amazon":True},
							plus={"archery":10}
							),
		missTemplate =  """ This isn't the {{node.goalBox.description}}!
							Go to {{node.goalBox.label}}""",
        page=			""" You chose Trojan! Your
							archery skills went up
							by {{node.change.plus['archery']}}!
							Now return to your Turma
							at the arena gates.""",
		goalBoxUid = garrisonBox.uid,
		nextNodeUid="gate1",
    )

	#count     123456789x123456789x123456

    ThroughSequence(
		uid =           "gate1",
		goalBoxUid =    gateBox.uid,
		nextNodeUid =   "trainingFork1",
		sequence = [
            """ You return to the
				gates and meet with
				members of your Turma.
				They are talking about
				a strategy tablet
				called the Ars Technica.""",
            """ You think about going
				to collect it from
				Victor, a groom visiting
				from Arbeia, but you
				still need to prepare
				for the games.""",
            """ You only have time to
				do so much before the
				games begin! Choose
				from the following
				options:""",
        ],
    )

	#4 training fork

    NodeFork(
        uid =   "trainingFork1",
        choices = {
            "arsTech1": """
            Collect the tablet
            from Victor at the fort.
            """,
            "epona1": """
            Make an offering to
            Epona at the garrison.
            """,
            "weapon1": """
            Train with your main
            weapon at the arena.
            """,
            }
			)

				#count     123456789x123456789x123456

    ThroughPage(
		uid="arsTech1",
		change =        SackChange(
							assign={"arstech":True},
							),
		missTemplate =  """ This isn't the {{node.goalBox.description}}!
							Go to {{node.goalBox.label}}""",
        page=			""" You track down Victor
							and he lets you read
							his Ars Technica tablet.
							INVESTIGATE the displays
							for info on tactics. This
							will be useful later...""",
		goalBoxUid = fortBox.uid,
		nextNodeUid="rest1",
    )

    ThroughPage(
		uid="epona1",
		change =        SackChange(
							plus={"horse":20},
							),
		missTemplate =  """ This isn't the {{node.goalBox.description}}!
							Go to {{node.goalBox.label}}""",
        page=			""" You return to your
							garrison and find the
							altar you brought with
							you from Senhouse.
							Make an offering of
							wine to Epona, increasing
							your horse skills by {{node.change.plus['horse']}}.""",
		goalBoxUid = garrisonBox.uid,
		nextNodeUid="rest1",
    )


    ConditionFork(
        uid=           "weapon1",
        condition =    "sack.archery >= 20",
        trueNodeUid=   "archery1",
        falseNodeUid=  "sword1",
    )


    ThroughPage(
		uid="archery1",
		change =        SackChange(
							plus={"archery":20},
							),
		missTemplate =  """ This isn't the {{node.goalBox.description}}!
							Go to {{node.goalBox.label}}""",
        page=			""" The arena is quiet
							before the games.
							You take the time to
							PRACTICE your archery,
							raising your skllls by
							{{node.change.plus['archery']}}.""",
		goalBoxUid = arenaBox.uid,
		nextNodeUid="rest1",
    )

    ThroughPage(
		uid="sword1",
		change =        SackChange(
							plus={"sword":20},
							),
		missTemplate =  """ This isn't the {{node.goalBox.description}}!
							Go to {{node.goalBox.label}}""",
        page=			""" The arena is quiet
							before the games.
							You take the time to
							PRACTICE your sword
							technique, raising
							your sklll to {{node.change.plus['archery']}}.""",
		goalBoxUid = arenaBox.uid,
		nextNodeUid="rest1",
    )


	# variables check (take out later)

    ThroughSequence(
		uid =           "rest1",
		goalBoxUid =    fortBox.uid,
		nextNodeUid =   "games1",
        sequence = [
            """ You take a short
				rest after your
				training. You think
				about the games later
				today and wonder
				how to approach them.""",
            """ Have you got the
				Ars Technica? {{sack.arstech}}.
				Horse skill level? {{sack.horse}}.
				Sword Skill level? {{sack.sword}}.
				Archery skill level? {{sack.archery}}""",
            """ You give your horse
				a ride around the training
				circuit to give him
				some air. RIDE THE
				HORSE in the gallery!
				Ready?""",
        ],
    )

    ThroughPage(
            uid = "games1",
            goalBoxUid = arenaBox.uid,
            page="""The arena is busy
            with people preparing
            for the games
            Your adventure has just
            begun!
            """,
            nextNodeUid ="gate1",
            )

if __name__ == "__main__":
    print("Loading emulator")
    emulator = ConsoleSiteEmulator(story=story)
    print("Running Emulator")
    emulator.run()

