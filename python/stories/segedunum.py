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
        "slaves": 0,
        "horses": 75,
        "men": 50,
        "swords": 150,
        "spears": 30,
        "arrows": 501,
        "uniforms": 50,
        "boots": 15,
        "victory": 0,
    }
)

with story:
    # populate with boxes

    messageBox = Box(uid="1", label="Box I", description="the Messengers")
    tableBox = Box(uid="2", label="Box II", description="the Table")
    mapBox = Box(uid="3", label="Box III", description="the Map")
    stablesBox = Box(uid="4", label="Box IV", description="the Stables")

    entranceBox = messageBox

    # count               123456789x123456789x123456

    # 1. MORNING TASKS

    ThroughSequence(
        uid="landing",
        change=SackChange(
            reset=story.startSack
        ),
        goalBoxUid=messageBox.uid,
        nextNodeUid="table1",
        sequence=[
            # 23456789x123456789x1234

            """ Welcome to Milecastles!
				Look for numbered boxes
				and hold your tag to
				progress the story...""",
            """ You are a treasurer at
                Segedunum Fort. There
                has been an outbreak of
                fighting along the
                wall...""",
            """	Other forts are asking
                for help with supplies.
                But don't forget to
                keep some of them back
                for yourself!...""",

        ],
    )

    ThroughSequence(
        uid="table1",
        goalBoxUid=tableBox.uid,
        nextNodeUid="map1",
        sequence=[
            # 23456789x123456789x1234
            """ You are in your
				quarters. The room is
				luxurious, and fine
				crafts surround you...""",
            """ On your table, you find
				a message asking you to
				send supplies urgently
				to several other
				forts...""",
            """ Go to Box III to
                see which forts
                need help.""",
        ],
    )

    ThroughSequence(
        uid="map1",
        change=SackChange(
            reset=story.startSack
        ),
        goalBoxUid=mapBox.uid,
        nextNodeUid="message1",
        sequence=[
            # 23456789x123456789x1234

            """ There is a large map
				here showing Hadrian's
				Wall and the forts
				that lie along it...""",
            """ Your clerk tells you
				that ARBEIA, CHESTERS
				& HOUSESTEADS have sent
				messengers. Meet them
				at Box I.""",
        ],
    )

    # TRADE FORK 1
    # 23456789x123456789x1234

    ThroughPage(
        uid="message1",
        page="""	You make your way to
					the other side of the
					fort where the
					messengers are waiting.
					They ask you to send...""",
        goalBoxUid=messageBox.uid,
        nextNodeUid="tradeFork1",
    )
    # 23456789x123456789x1234

    NodeFork(
        uid="tradeFork1",
        choices={
            "arbeia1": """	Horses to
								ARBEIA """,
            "corbridge1": """ Weapons to
								CHESTERS """,
            "housesteads1": """	Cavalrymen to
								HOUSESTEADS  """,
        },
        hideChoices={
            "arbeia1": "sack.horses<=50",
            "corbridge1": "sack.swords<=70",
        },
    )

    # HORSES
    # 23456789x123456789x1234

    ThroughPage(
        uid="arbeia1",
        missTemplate=""" You need to go to the
							GROUND FLOOR to the
							STABLES at {{node.goalBox.label}}""",
        page=""" You walk all the way to
					the stables and ask a
					groom how many horses
					we can spare.
					He suggests sending 25
					of our {{sack.horses}}
					horses.""",
        goalBoxUid=stablesBox.uid,
        nextNodeUid="horseFork1",
    )
    # 23456789x123456789x1234

    NodeFork(
        uid="horseFork1",
        choices={
            "arbeia2": """ Send 25 horses to
							ARBEIA""",
            "arbeia3": """ Send 50 horses to
							ARBEIA""",
        },
    )

    ThroughPage(
        uid="arbeia2",
        change=SackChange(
            minus={"horses": 25},
            plus={"slaves": 25},
        ),
        page= 		"""	You ask the groom to
							prepare {{node.change.minus['horses']}} horses
							to be sent to Arbeia.
							You send {{node.change.plus['slaves']}} slaves
							with the horses .""",goalBoxUid =messageBox.uid,
        nextNodeUid="rest1",
    )

    ThroughPage(
        uid="arbeia3",
        change=SackChange (
            minus={"horses":50},
            plus={"slaves":50},
        ),
        page=		"""	You ask the groom to
							prepare {{node.change.minus['horses']}} horses
							to be sent to Arbeia.
							You send {{node.change.plus['slaves']}} slaves
							with the horses.""",
        goalBoxUid =mapBox.uid,
        nextNodeUid="rest1",
    )

    # WEAPONS
    # 23456789x123456789x1234

    ThroughPage(
        uid="corbridge1",
        page=		"""	You ask the Decurion
							how many swords we can
							spare. He grumpily
							suggests 50 out of
							our stock of {{sack.swords}}.""",
        goalBoxUid=mapBox.uid,
        nextNodeUid="swordFork1",
    )
    # 23456789x123456789x1234

    NodeFork(
        uid="swordFork1",
        choices={
            "corbridge2": """	Send 50 swords to
								CHESTERS""",
            "corbridge3": """	Send 100 swords to
								CHESTERS""",
        },
    )

    ThroughPage(
        uid="corbridge2",
        change=SackChange(
            minus={"swords": 50},
            plus={"slaves": 5},
        ),
        page=			"""	You ask the Decurion
								to prepare {{node.change.minus['swords']}} swords
								to be sent to CHESTERS.
								It will take {{node.change.plus['slaves']}} slaves
								to deliver them...""",goalBoxUid =messageBox.uid,
        nextNodeUid="rest1",
    )
    # 23456789x123456789x1234

    ThroughPage(
        uid="corbridge3",
        change=SackChange (
            minus={"swords":100},
            plus={"slaves":10},
        ),
        page=			"""	You ask the Decurion
								to prepare {{node.change.minus['swords']}} swords
								to be sent to CHESTERS.
								It will take {{node.change.plus['slaves']}} slaves
								to deliver them...""",
        goalBoxUid =tableBox.uid,
        nextNodeUid="rest1",
    )

    # SOLDIERS
    # 23456789x123456789x1234

    ThroughPage(
        uid="housesteads1",
        page=	"""	You ask the officer how
						many cavalrymen we can
						send to HOUSESTEADS.
						He suggests we don't
						send any of our
						{{sack.men}} cavalry!""",
        goalBoxUid=tableBox.uid,
        nextNodeUid="soldierFork1",
    )
    # 23456789x123456789x1234

    NodeFork(
        uid="soldierFork1",
        choices={
            "housesteads2": """	Send 0 cavalry to
									HOUSESTEADS """,
            "housesteads3": """	Send 25 cavalry to
									HOUSESTEADS """,
        },
    )
    # 23456789x123456789x1234

    ThroughPage(
        uid="housesteads2",
        change=SackChange(
            plus={"slaves": 25},
            minus={"uniforms": 25},
        ),
        page=				"""	You don't want to spare
									any of your cavalry, so
									you send {{node.change.plus['slaves']}} slaves,
									wearing {{node.change.minus['uniforms']}} cloaks,
									instead...""",goalBoxUid =messageBox.uid,
        nextNodeUid="rest1",
    )
    # 23456789x123456789x1234


    ThroughPage(
        uid="housesteads3",
        change=SackChange (
            minus={"men":25},
            plus={"horses":25},
        ),
        page=				"""	You send {{node.change.minus['men']}} cavalry
									along with {{node.change.minus['men']}} horses
									to HOUSESTEADS. It's
									risky, but HOUSESTEADS
									is an important fort!""",
        goalBoxUid=mapBox.uid,
        nextNodeUid="rest1",
    )

    # REST 1
    # 23456789x123456789x1234

    ThroughSequence(
        uid="rest1",
        goalBoxUid=tableBox.uid,
        nextNodeUid="map2",
        sequence=[
            """ You stop for a lunch and
				think about your days
				with a cavalry. You
				miss defending the wall
				but the small feast in
				front of you makes up
				for it...""",
            """ Before going back to
				work, you check your
				ledger. You have:
				{{sack.men}} cavalry
				{{sack.horses}} horses
				{{sack.swords}} swords """,
            """ You had to buy {{sack.slaves}}
                new slaves to replace the
                ones you sent to other
                forts. That won't be
                cheap...""",
        ],
    )

    ThroughPage(
        uid="map2",
        page="""	You walk back over to
					look at the map and
					find that another
					group of messengers
					have arrived...""",
        goalBoxUid=mapBox.uid,
        nextNodeUid="message2",
    )

    # TRADE FORK 2
    # 23456789x123456789x1234

    ThroughPage(
        uid="message2",
        page="""	The messengers look
					tired from their
					long ride. They ask
					you to...""",
        goalBoxUid=messageBox.uid,
        nextNodeUid="tradeFork2",
    )
    # 23456789x123456789x1234

    NodeFork(
        uid="tradeFork2",
        choices={
            "arbeia5": """	Send boots
								to ARBEIA """,
            "corbridge5": """ Send spears to
								CHESTERS """,
            "housesteads5": """	Send arrows to
								HOUSESTEADS  """,
        },
    )

    # BOOTTS
    # 23456789x123456789x1234

    ThroughPage(
        uid="arbeia5",
        missTemplate=""" You need to go to the
							GROUND FLOOR to the
							STABLES at {{node.goalBox.label}}""",
        page=""" You walk to the stables
					and check how many
					pairs of boots are there.
					PEW!!! They've not been
					cleaned for months!!!...""",
        goalBoxUid=stablesBox.uid,
        nextNodeUid="uniformFork1",
    )
    # 23456789x123456789x1234

    NodeFork(
        uid="uniformFork1",
        choices={
            "arbeia6": """ Send 5 boots
							to ARBEIA""",
            "arbeia7": """ Send 15 boots
							to ARBEIA""",
        },
    )

    ThroughPage(
        uid="arbeia6",
        change=SackChange(
            minus={"boots": 5},
            plus={"slaves": 1},
        ),
        page= 		"""	You ask the groom to
							prepare {{node.change.minus['boots']}} boots
							to be sent to ARBEIA.
							It takes {{node.change.plus['slaves']}} slaves
							to carry them because of
							the awful smell.""",goalBoxUid =messageBox.uid,
        nextNodeUid="rest2",
    )

    ThroughPage(
        uid="arbeia7",
        change=SackChange (
            minus={"boots":15},
            plus={"slaves":5},
        ),
        page = 	"""	You ask the groom to
							prepare {{node.change.minus['boots']}} boots
							to be sent to ARBEIA.
							It takes {{node.change.plus['slaves']}} slaves
							to carry them because of
							the appalling smell.""",
        goalBoxUid =mapBox.uid,
        nextNodeUid="rest2",
    )

    # SPEARS
    # 23456789x123456789x1234

    ThroughPage(
        uid="corbridge5",
        page=		"""	You ask the Decurion how
							many spears we can send.
							He says that there are
							only {{sack.swords}} available.""",
        goalBoxUid = mapBox.uid,
        nextNodeUid="spearFork1",
    )
    # 23456789x123456789x1234

    NodeFork(
        uid =   "spearFork1",
        choices = {
            "corbridge6":   """	Send 10 spears to
								CHESTERS""",
            "corbridge7":   """	Send 30 spears to
								CHESTERS""",
        },
    )

    ThroughPage(
        uid="corbridge6",
        change= SackChange (
            minus={"spears" :10},
            plus={"slaves" :3},
        ),
        page=				"""	You ask the Decurion
								to prepare {{node.change.minus['spears']}} spears
								to be sent to CHESTERS.
								It takes {{node.change.plus['slaves']}}
								slaves to carry them.""",
        goalBoxUid = messageBox.uid,
        nextNodeUid="rest2",
    )

    ThroughPage(
        uid="corbridge7",
        change= SackChange (
            minus={"spears" :30},
            plus={"slaves" :8},
        ),
        page=				"""	You ask the Decurion
								to prepare {{node.change.minus['spears']}} spears
								to be sent to CHESTERS.
								It takes {{node.change.plus['slaves']}}
								slaves to carry them.""",
        goalBoxUid = tableBox.uid,
        nextNodeUid="rest2",
    )

    # ARROWS
    # 23456789x123456789x1234

    ThroughPage(
        uid="housesteads5",
        page=		"""	The Decurion is now
						off-duty. You will
						have to guess how many
						arrows are here as it
						will take FOREVER to
						count them...""",
        goalBoxUid = tableBox.uid,
        nextNodeUid="arrowFork1",
    )
    # 23456789x123456789x1234

    NodeFork(
        uid =   "arrowFork1",
        choices = {
            "housesteads6":  	"""	Send 500 arrows to
									HOUSESTEADS """,
            "housesteads7":    	"""	Send 300 arrows to
									HOUSESTEADS """,
        },
    )
    # 23456789x123456789x1234

    ThroughPage(
        uid="housesteads6",
        change= SackChange (
            minus={"arrows" :500},
            plus={"slaves" :5},
        ),
        page=					"""	You bundle up a big
									pile of {{node.change.minus['arrows']}} arrows
									and send them off with
									the {{node.change.plus['slaves']}}.""",
        goalBoxUid = messageBox.uid,
        nextNodeUid="rest2",
    )

    ThroughPage(
        uid="housesteads7",
        change= SackChange (
            minus={"arrows" :300},
            plus={"slaves" :3},
        ),
        page=					"""	You bundle up a medium
									pile of {{node.change.minus['arrows']}} arrows
									and send them off with
									{{node.change.plus['slaves']}} reliable slaves...""",
        goalBoxUid = mapBox.uid,
        nextNodeUid="rest2",
    )

    # REST 2
    # 23456789x123456789x1234

    ThroughSequence(
        uid =           "rest2",
        goalBoxUid =    tableBox.uid,
        nextNodeUid =   "map3",
        sequence = [
            """ You're feeling very
				tired from all this
				work and start to
				think about your bed.
				Wait a minute, what's
				that noise?... """,
            """	A BATTLE HAS BROKEN
                OUT! INVADERS FROM THE
                WEST!! You need to
                check we have enough
                supplies to win...""",
            """ The ledger says:
				{{sack.uniforms}} cloaks
				{{sack.spears}} spears
				{{sack.arrows}} arrows...""",
            """ {{sack.swords}} swords
                {{sack.men}} cavalry
                {{sack.horses}} arrows
                and {{sack.boots}} boots
                ...""",
            """	You need to get to the
                stables and hand out
                supplies to the cavalry
                ...""",
        ],
    )

    ThroughSequence(
        uid="map3",
        goalBoxUid = stablesBox.uid,
        nextNodeUid="supplyFork1",
        sequence=	[
            """	You run to the
                stables and start to
                organise the handing
                out of supplies. First
                let's check on HORSES...""",
        ]
    )
    # 23456789x123456789x1234

    # HORSE CHECK

    ConditionFork(
        uid=           "supplyFork1",
        condition =    "sack.horses >= 25 ",
        trueNodeUid=   "goodHorse1",
        falseNodeUid=  "badHorse1",
    )
    # 23456789x123456789x1234

    ThroughPage(
        uid="goodHorse1",
        change =        SackChange(
            plus={"victory" :1},
        ),
        page=			""" You have {{sack.horses}}
							horses - enough for
							all your cavalry to ride
							in style! You won
							{{node.change.plus['victory']}} victory point!...""",
        goalBoxUid = stablesBox.uid,
        nextNodeUid="supply2",
    )

    ThroughPage(
        uid="badHorse1",
        page=			""" You have {{sack.horses}}
							horses - not enough for
							your cavalry to ride
							out on :( Your chances
							of winning the battle
							are not good...""",
        goalBoxUid = stablesBox.uid,
        nextNodeUid="supply2",
    )

    # sword CHECK

    ThroughPage(
        uid="supply2",
        page=		"""	Now to check on
						the SWORDS...""",
        goalBoxUid = stablesBox.uid,
        nextNodeUid="supplyFork2",
    )

    ConditionFork(
        uid=           "supplyFork2",
        condition =    "sack.swords >= 50 ",
        trueNodeUid=   "goodSword1",
        falseNodeUid=  "badSword1",
    )

    ThroughPage(
        uid="goodSword1",
        change =        SackChange(
            plus={"victory" :1},
        ),
        page=			""" You have {{sack.swords}}
							swords - enough for
							your cavalry to slash
							the enemy! You won
							{{node.change.plus['victory']}} victory point!...""",
        goalBoxUid = stablesBox.uid,
        nextNodeUid="supply3",
    )

    ThroughPage(
        uid="badSword1",
        page=			""" You have {{sack.horses}}
							swords - not enough for
							share 1 between 2
							soldiers :( Your chances
							of winning the battle
							are shrinking...""",
        goalBoxUid = stablesBox.uid,
        nextNodeUid="supply3",
    )

    # CAVALRY check

    ThroughPage(
        uid="supply3",
        page=		"""	Now to check on
						the CAVALRY...""",
        goalBoxUid = mapBox.uid,
        nextNodeUid="supplyFork3",
    )

    ConditionFork(
        uid=           "supplyFork3",
        condition =    "sack.men >= 25 ",
        trueNodeUid=   "goodCav1",
        falseNodeUid=  "badCav1",
    )

    ThroughPage(
        uid="goodCav1",
        change =        SackChange(
            plus={"victory" :2},
        ),
        page=			""" You have {{sack.men}}
							cavalry - enough for
							you to chase the enemy
							back along the wall!
							You won {{node.change.plus['victory']}}
							victory points!...""",
        goalBoxUid = tableBox.uid,
        nextNodeUid="supply4",
    )

    ThroughPage(
        uid="badCav1",
        page=			""" You have {{sack.men}}
							cavalry - not enough to
							even scare the enemy!
							Your chances of winning
							the battle are tiny...""",
        goalBoxUid = tableBox.uid,
        nextNodeUid="supply4",
    )

    # arrows check

    ThroughPage(
        uid="supply4",
        page=		"""	Now to check on
						the ARROWS...""",
        goalBoxUid = mapBox.uid,
        nextNodeUid="supplyFork4",
    )

    ConditionFork(
        uid=           "supplyFork4",
        condition =    "sack.arrows >= 2 ",
        trueNodeUid=   "goodArrow",
        falseNodeUid=  "badArrow",
    )

    ThroughPage(
        uid="goodArrow",
        change =        SackChange(
            plus={"victory" :1},
        ),
        page=			""" You have {{sack.arrows}}
							swords - enough to rain
							pointy fear on the enemy!
							You won {{node.change.plus['victory']}}""",
        goalBoxUid = mapBox.uid,
        nextNodeUid="endFork1",
    )

    ThroughPage(
        uid="badArrow",
        page=			""" You have {{sack.arrows}}
							arrows - you've given
							too many away! :(
							Your chances
							of winning the battle
							are vanishing...""",
        goalBoxUid = mapBox.uid,
        nextNodeUid="endFork1",
    )
    # endfork1

    ConditionFork(
        uid=           "endFork1",
        condition =    "sack.victory >= 3",
        trueNodeUid=   "goodEnd1",
        falseNodeUid=  "badEnd1",
    )

    ThroughPage(
        uid="goodEnd1",
        page=			""" You've  saved the day
							with your careful
							trading! Your
							commander applauds
							you! Now to check
							how much we spent...""",
        goalBoxUid = messageBox.uid,
        nextNodeUid="endFork2",
    )

    # 23456789x123456789x1234

    ThroughPage(
        uid="badEnd1",
        page=			""" You have lost the
							battle by giving away
							too many supplies!!
							Your commander scolds
							you! Now to check the
							bank... uh-oh...""",
        goalBoxUid = messageBox.uid,
        nextNodeUid="endFork2",
    )

    # BANK fork

    ConditionFork(
        uid=           "endFork2",
        condition =    "sack.slaves <= 60",
        trueNodeUid=   "goodEnd2",
        falseNodeUid=  "badEnd2",
    )

    ThroughPage(
        uid="goodEnd2",
        page=			""" You have sent away
							a very sensible
							total of {{sack.slaves}} slaves
							for transporting goods.
							Well within our budget!
							Your commander applauds
							you!...""",
        goalBoxUid = tableBox.uid,
        nextNodeUid="end3",
    )
    # 23456789x123456789x1234
    # 23456789x123456789x1234

    ThroughPage(
        uid="badEnd2",
        page=			""" You've spent an fortune
							on slaves!! Do you know
							how much {{sack.slaves}} slaves
							cost these days?? You'll
							have to clean the boots
							for a long time to make
							up for this...""",
        goalBoxUid = tableBox.uid,
        nextNodeUid="end3",
    )

    ThroughPage(
        uid="end3",
        page=			""" You've completed the
							game! TAP HERE to
							try for a different
							ending or visit
							another museum to play
							more Milecastles!""",
        goalBoxUid = tableBox.uid,
        nextNodeUid="landing",
    )