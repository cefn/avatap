from milecastles import Story, Box, ThroughPage, ThroughSequence, ConditionFork, NodeFork, SackChange

# inspects the module to figure out the story name (e.g. corbridge)
storyName = __name__.split(".")[-1]

# create story
story = Story(
	uid=storyName,
	version="0.1.0",
	# choose an alternative startNodeUid and startSack for debugging
	# startNodeUid = "stoneFork",
	startNodeUid="landing",
	startSack={
		"money": 0,
		"points": 0,
		"water": False,
		"polish": False,
		"harness": False,
		"dung": False,
		"beads": False,
		"fire": False,
		"feed": False,
	}
)

with story:
	# populate with boxes

	quartersBox = Box(uid="1", label="Box I", description="your quarters")
	storesBox = Box(uid="2", label="Box II", description="the Storeroom")
	barracksBox = Box(uid="3", label="Box III", description="the Barracks")

	entranceBox = quartersBox

	# THIS IS THE UPDATED VERSION FOR ALEX TO CHECK

	# 1. INTRO / MORNING TASKS
	# 123456789012345678901234

	ThroughSequence(
		uid="landing",
		change=SackChange(
			reset=story.startSack
		),
		goalBoxUid=quartersBox.uid,
		nextNodeUid="stores0",
		sequence=[
			""" Welcome to Milecastles!
				Look for numbered boxes
				and hold your tag to
				progress the story...""",
			""" You are a slave to
				the commanding officer
				at Arbeia fort. The
				fort is under-staffed
				& your quest is to fill
				in for a sick groom....""",
			""" You've even been promised
				Denarii for each task!
				Even though earning money
				is normally out of the
				question for slaves...""",
			""" You are in your quarters.
				Walk over to BOX II
				on the other side of the
				museum to get started.""",
		],
	)

	ConditionFork(
		uid="stores0",
		condition="sack.dung == True or sack.water == True",
		trueNodeUid="rest1",
		falseNodeUid="stores1",
	)
	# 123456789012345678901234

	ThroughPage(
		uid="stores1",
		missTemplate=""" This isn't the storeroom!
							Go to {{node.goalBox.label}}""",
		page=		""" You let yourself into the
							storeroom. It's dark and
							musty in here. You find a
							note with today's list of
							jobs waiting for you.""",goalBoxUid =storesBox.uid,
		nextNodeUid="storesFork1",
	)
	# 123456789012345678901234

	NodeFork(
		uid="storesFork1",
		choices={
			"dung1": """ Get your broom and clean
								the stables""",
			"water1": """ Collect water from
								the well""",
		},
		hideChoices={
			"water1": "sack.water==True",
			"dung1": "sack.dung==True",
		},
	)
	# 123456789012345678901234


	ThroughSequence(
		uid="water1",
		goalBoxUid=barracksBox.uid,
		nextNodeUid="water2",
		sequence=[
			""" You walk across the
				courtyard in the rain.
				Pretend to FETCH the
				water from the well
				into a BUCKET...""",
			""" Keep going, you'll
				need a lot more
				than one bucket!
				...""",
		],
	)
	# 123456789012345678901234

	ThroughPage(
		uid="water2",
		change=SackChange(
			assign={"water": True},
			plus={"money": 10},
		),
		missTemplate=""" Stop slacking!!
							Go to {{node.goalBox.label}}""",
		page=		""" Your bucket is now full.
							Pretend to CARRY the
							heavy bucket back to the
							main building.
							Don't spill any!
							You earned {{node.change.plus['money']}} Denarii""",
        goalBoxUid =barracksBox.uid,
		nextNodeUid="stores0",
	)
	# 123456789012345678901234

	ThroughPage(
		uid="dung1",
		missTemplate=""" Stop slacking!!
							Go to {{node.goalBox.label}}""",
		page=		""" You quickly go to your
							quarters to find your
							broom. It's behind some
							old animal skins.
							Now head outside
							to the STABLES.""",goalBoxUid =quartersBox.uid,
		nextNodeUid="dung2",
	)
	# 123456789012345678901234

	ThroughSequence(
		uid="dung2",
		goalBoxUid=barracksBox.uid,
		missTemplate=""" Stop slacking!!
							Go to {{node.goalBox.label}}""",
		nextNodeUid="dung3",
		sequence=[
			""" You walk across the
				courtyard, saying hello
				to other slaves on your
				way. You head to the
				front of the barracks
				where the stables are
				found...""",
			""" Pretend to SWEEP the
				horse droppings into
				a corner. HOLD YOUR NOSE
				with the other hand...""",
			""" You missed a bit!
				Sweep some more!
				The horses must have
				been eating a lot...""",
		],
	)
	# 123456789012345678901234

	ThroughPage(
		uid="dung3",
		change=SackChange(
			assign={"dung": True},
			plus={"money": 5},
		),
		missTemplate=""" Stop slacking!!
							Go to {{node.goalBox.label}}""",
		page=		"""	The stable is now clean!
							Put your brush down and
							walk back to the main
							building. You earned
							{{node.change.plus['money']}} Denarii.""",
        goalBoxUid =barracksBox.uid,
		nextNodeUid="stores0",
	)
	# 123456789012345678901234

	ThroughPage(
		uid="rest1",
		missTemplate=""" Time for a break - go to
							your quarters at {{node.goalBox.label}}""",
		page=		""" You take a short rest in
							your quarters. You think
							about the {{sack.money}} Denarii
							you've earned so far.
							It's good to sit down...""",
		# 123456789012345678901234
        goalBoxUid =quartersBox.uid,
		nextNodeUid="stores3",
	)

	# 2. MORNING TASKS pt 2
	# 123456789012345678901234

	ThroughPage(
		uid="stores5",
		missTemplate=""" This isn't the storeroom!
							Go to {{node.goalBox.label}}.""",
		page= 		""" What's next?
							Go to {{node.goalBox.label}}
							...""",goalBoxUid = storesBox.uid,
		nextNodeUid="stores3",
	)

	ConditionFork(
		uid=           "stores3",
		condition =    "sack.fire == True or sack.feed == True",
		trueNodeUid=   "rest2",
		falseNodeUid=  "stores4",
	)
	# 123456789012345678901234

	ThroughPage(
		uid=	"stores4",
		page=	""" You let yourself back
					into the storeroom.
					It's still dark and musty
					in here (and there are
					spiders). You find a new
					list of jobs to complete.""",
		goalBoxUid = storesBox.uid,
		nextNodeUid="storesFork2",
	)
	# 123456789012345678901234


	NodeFork(
		uid =   "storesFork2",
		choices = {
			"feed1":    """ Collect feed for the
							cavalry horses""",
			"fire1":   	""" Make up a fire in the
							barracks""",
		},
		hideChoices = {
			"fire1":   "sack.fire==True",
			"feed1":    "sack.feed==True",
		},
	)

	# 123456789012345678901234


	ThroughSequence(
		uid =           "fire1",
		goalBoxUid =    barracksBox.uid,
		missTemplate =  "Stop slacking!! Go to {{node.goalBox.label}}",
		nextNodeUid =   "fire2",
		sequence = [
			""" You walk across the
				courtyard in the mud.
				You need to SCRAPE your
				boots before carrying
				on...""",
			""" You find the wood store
				next to the Barracks...
				Pretend to GATHER the
				wood into a CART...""",
			""" Keep going, you'll need
				a lot more than that!
				...""",
			"""	Now PUSH the CART inside
				the barracks and pretend
				to BUILD a fire in one
				of the fireplaces...""",
		],
	)
	# 123456789012345678901234


	ThroughPage(
		uid="fire2",
		change =        SackChange(
			assign={"fire" :True},
			plus={"money" :5},
		),
		page=""" When the fire is hot,
				 head back to the
				 storeroom. You earned
				 {{node.change.plus['money']}} Denarii.""",
		goalBoxUid = barracksBox.uid,
		nextNodeUid="stores5",
	)
	# 123456789012345678901234


	ThroughPage(
		uid="feed1",
		page=""" You quickly go to
				 your quarters to
				 find an empty sack.
				 Now go back outside
				 to the STABLES.""",
		goalBoxUid = quartersBox.uid,
		nextNodeUid="feed2",
	)
	# 123456789012345678901234

	ThroughSequence(
		uid =           "feed2",
		goalBoxUid =    barracksBox.uid,
		missTemplate =  """ Stop slacking!!
							Go to {{node.goalBox.label}}""",
		nextNodeUid =   "feed3",
		sequence = [
			""" You walk across the
				courtyard again.
				(Aren't your feet
				getting sore?) and go
				into the stables in
				front of the Barracks...""",
			""" Pretend to SHOVEL the
				horse feed into a sack.
				COUNT to 15 in Roman
				numerals to make sure
				that you have enough...""",
		],
	)

	# 123456789012345678901234


	ThroughPage(
		uid="feed3",
		change =        SackChange(
			assign={"feed" :True},
			plus={"money" :10},
		),
		page=""" Those horses should be
				 nice and full now.
				 Put your sack down down
				 and walk back to the
				 storeroom. You earned
				 {{node.change.plus['money']}} Denarii""",
		goalBoxUid = barracksBox.uid,
		nextNodeUid="stores5",
	)

	# 123456789012345678901234


	ThroughSequence(
		uid="rest2",
		goalBoxUid = quartersBox.uid,
		nextNodeUid="rest3",
		sequence=	[
			""" You take a another rest
				in your quarters and
				talk to your friend
				Victor. 'You look
				REALLY tired!!...""",
			""" 'Have you:
				FED the horses?'
				You answer: {{sack.feed}}!
				FETCHED the water?
				You answer: {{sack.water}}!
				MADE the fire?
				You answer: {{sack.fire}}!""",
			""" 'SWEPT the stables?'
				You answer: {{sack.dung }}!
				'And how much have you
				earned?'
				I've earned an amazing
				{{sack.money}} Denarii! """,
		]
	)

	# 123456789012345678901234


	# 3. PM TASKS / HORSE RELATED

	ThroughPage(
		uid="rest3",
		change =   SackChange(
			minus={"money" :3},
		),
		page="""	You share some bread &
					cheese that you bought
					for {{node.change.minus['money']}} Denarii.
					Now back to work!""",
		goalBoxUid = quartersBox.uid,
		nextNodeUid="stores6",
	)

	ThroughPage(
		uid="stores6",
		page=""" It's still musty in
				 the storeroom.
				 Was that a rat?
				 You're a bit tired,
				 but can't quite finish
				 work yet...""",
		goalBoxUid = storesBox.uid,
		nextNodeUid="storesFork3",
	)

	NodeFork(
		uid =   "storesFork3",
		choices = {
			"horse1":   """	Find your master at the
							barracks""",
			"sleep1":   """	I'm tired!! Go to bed
							and end the game""",
		},
	)
	# 123456789012345678901234

	ThroughSequence(
		uid =           "sleep1",
		goalBoxUid =    quartersBox.uid,
		missTemplate =  """ This isn't your quarters
							Go to {{node.goalBox.label}}""",
		nextNodeUid =   "badEnd1",
		sequence = [
			""" Your bed looks too
				comfortable...
				Maybe just a quick nap.
				No one will notice...""",
			""" YAWN!! You wake up
				MUCH later. Can you
				CHECK the position
				of the sun to work out
				the time?""",
		],
	)
	#		123456789012345678901234

	ThroughPage(
		uid="badEnd1",
		change =		SackChange(
			minus={"money" :5},
		),
		page="""Your master has left
				the fort! You will lose
				{{node.change.minus['money']}} Denarii
				of your pay, but at least
				you won't have to cross
				the courtyard again! """,
		goalBoxUid = quartersBox.uid,
		nextNodeUid="badEnd2",
	)
	# 123456789012345678901234

	ThroughPage(
		uid="badEnd2",
		page="""	The END! How did you
					find life as a groom?
					You made {{sack.money}} Denarii.
					HOLD TAG to play again or
					visit another museum to
					play another character.""",
		goalBoxUid = quartersBox.uid,
		nextNodeUid="landing",
	)

	# 123456789012345678901234


	# 4. Grooming the horse

	ThroughPage(
		uid="horse1",
		missTemplate =  """ This isn't the Barracks!
							Go to {{node.goalBox.label}}""",
		page=			""" You cross the courtyard.
							Your master is waiting
							at the barracks...""",
		goalBoxUid = barracksBox.uid,
		nextNodeUid="horse2",
	)
	# 123456789012345678901234

	ThroughPage(
		uid="horse2",
		change=		SackChange(
			plus={"money" :10},
		),
		missTemplate =  """	This isn't the Barracks!
							Go to{{node.goalBox.label}}""",
		page=""" Your master is happy!!
				 'What a great job you've
				 done! Here's a bonus of
				 {{node.change.plus['money']}} Denarii!'
				 ...'""",
		goalBoxUid = barracksBox.uid,
		nextNodeUid="uniform1",
	)
	# 123456789012345678901234

	ThroughPage(
		uid="uniform1",
		missTemplate =  """	This isn't the Barracks!
							Go to{{node.goalBox.label}}""",
		page=	""" 'Help to get me and my
					horse Regalis looking
					smart for the Troy Games!
					Quickly! I'm late!!''""",
		goalBoxUid = barracksBox.uid,
		nextNodeUid="uniformFork",
	)

	NodeFork(
		uid =   "uniformFork",
		choices = {
			"harness1":   """	'Clean my harness!
								Quickly!'""",
			"armour1":    """	'Polish my armour!
								Pronto!""",
		},
		hideChoices = {
			"harness1":   	  "sack.harness==True",
			"armour1":        "sack.polish==True",
		},
	)
	# 123456789012345678901234

	ThroughSequence(
		uid =           "harness1",
		goalBoxUid =    storesBox.uid,
		nextNodeUid =   "harness2",
		sequence = [
			""" You walk back to the
				stores. Aren't your feet
				getting tired yet?
				You need to find the
				scrubbing brush...""",
			""" Here it is. Pretend to
				SCRUB the harness.
				LOOK for other CAVALRY
				items in the museum,
				then come back...""",
		],
	)
	# 123456789012345678901234

	ThroughPage(
		uid="harness2",
		change =        SackChange(
			assign={"harness" :True},
			plus={"money" :10},
		),
		missTemplate =  """ This isn't the Barracks!
							Go to {{node.goalBox.label}}""",
		page=			""" The harness looks good!
							you've earned {{node.change.plus['money']}} Denarii.
							Looking closer, you
							notice a split. I wonder
							if I can find something
							to fix it in my quarters?""",
		goalBoxUid = storesBox.uid,
		nextNodeUid="wander1",
	)
	# 123456789012345678901234

	ThroughSequence(
		uid =           "armour1",
		change =        SackChange(
			assign={"polish" :True},
			plus={"money" :5},
		),
		goalBoxUid =    quartersBox.uid,
		nextNodeUid =   "uniform2",
		sequence = [
			""" EXPLORE the BARRACKS to
				LOOK for your tools and
				polish. Hmm, where did
				I leave them?""",
			""" Here they are...
				Pretend to HAMMER the
				dents out of the
				armour. Then POLISH
				the metal...""",
			""" Keep going, it's not
				clean yet! That's it!
				...""",
		],
	)

	# 123456789012345678901234


	ThroughSequence(
		uid =           "wander1",
		change =        SackChange(
			assign={"beads" :True},
		),
		goalBoxUid =    quartersBox.uid,
		nextNodeUid =   "uniform2",
		sequence = [
			""" You walk around your
				quarters for a while.
				Kicking an old barrel,
				you see something
				glinting. What is it?
				...""",
			""" Glass beads! Those
				will be perfect for
				covering the harness!""",
			"""	The harness looks
				perfect. Your master
				will be amongst the
				most well-dressed
				at the Trojan games...""",
		],
	)

	ConditionFork(
		uid=           "uniform2",
		condition =    "sack.polish == True and sack.harness == True",
		trueNodeUid=   "goodEnd1",
		falseNodeUid=  "uniform1",
	)
	# 123456789012345678901234

	ThroughPage(
		uid="goodEnd1",
		page=""" 	Your master is waiting
					outside of the storeroom.""",
		goalBoxUid = storesBox.uid,
		nextNodeUid="goodEnd2",
	)
	# 123456789012345678901234

	ThroughSequence(
		uid =           "goodEnd2",
		goalBoxUid =    storesBox.uid,
		nextNodeUid =   "goodEnd3",
		sequence = [
			""" 'Are you done yet?
				I have to get riding!
				Let me take a look...
				Did you clean my Harness?
				Answer: {{sack.harness}}
				...""",
			""" 'Did you put these fancy
				beads on there?'
				Answer: {{sack.beads}}
				'Did you repair my
				dented old armour?'
				Answer: {{sack.polish}}""",
			""" 'Well, I'm certainly
				going to be the toast
				of the Troy games!
				Please take this
				20 Denarii as a bonus!'""",
			""" He rides off to the
				West, whilst you go
				back to your quarters
				to count your pay.""",
		]
	)

	# 123456789012345678901234

	ThroughPage(
		uid =           "goodEnd3",
		goalBoxUid =    quartersBox.uid,
		change = SackChange(
			trigger = "sack.money >= 35",
			plus  =     {"money" :20},
		),
		page = """
			{% if node.change.triggered %}
				{% if node.change.completed %}
					With the bonus, I now
					have {{sack.money}} Denarii.
					Enough to buy my own
					pony and harness!
					That was the best
					day's work ever!
		   {% else %}
					OK, I've now got
					{{sack.money}} Denarii!
					Enough to buy some of
					new clothes and food.
					Not very exciting...
			{% endif %}
			{% else %}
					OK, I've now got
					{{sack.money}} Denarii!
					Enough to buy some of
					new clothes and food.
					Not very exciting...

			{% endif %}
		""",
		nextNodeUid = "goodEnd4",
	)
	# 123456789012345678901234

	ThroughPage(
		uid="goodEnd4",
		page=""" 	Now you can take a rest!
					LIFT and HOLD your TAG
					here to play again or go
					to another museum to play
					as a different character!""",
		goalBoxUid = quartersBox.uid,
		nextNodeUid="landing",
	)