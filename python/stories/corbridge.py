from engines.console import ConsoleSiteEmulator
from milecastles import Story, Box, ThroughPage, ThroughSequence, ConditionFork, NodeFork, SackChange

storyName = "corbridge"

# create story
story = Story(
    uid=storyName,
    # choose an alternative startNodeUid and startSack for debugging
    # startNodeUid = "stoneFork",
    startNodeUid="landing",
    startSack={
        "money": 100,
        "smithAnger": False,
        "stone": False,
        "sharp": False,
        "inspire": False,
        #removed points as money left is your score
        "afternoon": False,
    }
)

with story:
    # populate with boxes

    smithBox = Box(uid="1", label="Box I", description="the Blacksmith")
    workshopBox = Box(uid="2", label="Box II", description="the Workshop")
    tombBox = Box(uid="3", label="Box III", description="the Tomb")
    quarryBox = Box(uid="4", label="Box IV", description="the Quarry")
    entranceBox = smithBox

    # BOX I
    # 1a - intro / landing

    ThroughSequence(
        uid="landing",
        change=SackChange(
            reset=story.startSack
        ),
        goalBoxUid=smithBox.uid,
        nextNodeUid="workshop1",
        sequence=[
            """ Welcome to Milecastles!
                Look for numbered boxes
                and hold your tag to
                progress the story...""",
            """ You are a stonemason
                working at the military
                base at Corbridge...""",
            """ Your quest is to get
                materials, tools and
                inspiration to complete
                the tombstone....""",
            """ You have an advance of
                {{sack.money}} Denarii
                for materials.
                Spend it wisely...""",
        ],
    )

    # 1b Blacksmith am/pm
    ThroughPage(
        uid="smith1",
        missTemplate="""This isn't
        {{node.goalBox.description}}!
        Go to {{node.goalBox.label}}""",
        page="""You walk across the fort
				to the blacksmith's
				workshop. A sign says
				'Half-day closing today'""",
        goalBoxUid=smithBox.uid,
        nextNodeUid="sharpening",
    )

    ConditionFork(
        uid="sharpening",
        condition="sack.afternoon == True",
        trueNodeUid="sharpeningSuccess",
        falseNodeUid="sharpeningFailure",
    )

    ThroughPage(
        uid="sharpeningSuccess",
        change=SackChange(
            trigger="sack.sharp == False",
            assign={"sharp": True},
            minus={"money": 15},
        ),
        goalBoxUid=smithBox.uid,
        page="""
        {% if node.change.triggered %}
            {% if node.change.completed %}
                It's now the afternoon
                and the blacksmith is
                ready for you.
                Sharpening costs
                {{node.change.minus['money']}} Denarii.
                You have {{sack.money}} Denarii.
            {% else %}
                You don't have enough
                money to sharpen your
                tools.
            {% endif %}
        {% else %}
				You already sharpened
				your tools.
        {% endif %}
        """,
        nextNodeUid="sharpened",
    )

    ThroughPage(
            uid="sharpened",
            missTemplate="""This isn't
            {{node.goalBox.description}}!
            Go to {{node.goalBox.label}}""",
            page="""Look at the tools in
            the display and PRETEND
            to sharpen a spearhead.
            With sharp tools you can
            add more detail to the
            carving...""",
            goalBoxUid=smithBox.uid,
            nextNodeUid="fromSmith",
            )

    # Now our sharpening fail
    ThroughPage(
        uid="sharpeningFailure",
        missTemplate="""This isn't
        {{node.goalBox.description}}!
        Go to {{node.goalBox.label}}""",
        change=SackChange(
            assign={"smithAnger": True},
        ),
        page="""
        The Blacksmith is
        furious!
        'You're banned...!'
        No sharp tools
        for you...
        """,
        goalBoxUid=smithBox.uid,
        nextNodeUid="workshop1",
    )

    # BOX II
    # 2a Morning / First Workshop Fork

    ThroughPage(
        uid="workshop1",
        missTemplate="""To begin work,
        go to {{node.goalBox.label}}.""",
        page="""You are in your
		workshop.It's early, but
        you will have to work
        quickly to complete the
        carving...""",
        goalBoxUid=workshopBox.uid,
        nextNodeUid="workshop2",
    )

    NodeFork(
        uid="workshop2",
        choices={
            "smith1": """Go to the
            blacksmith""",
            "stone1": """Go outside to the
            quarry""",
            "inspire1": """Look for
            inspiration""",
        },
        hideChoices={
            "smith1": "sack.sharp==True",
            "stone1": "sack.stone==True",
            "smith1": "sack.smithAnger==True",
        },
    )

    # 2b Afternoon / Second Workshop Fork

    ThroughSequence(
        uid="workshop3",
        goalBoxUid=workshopBox.uid,
        nextNodeUid="firstSnack",
        sequence=[
            """ You've done a good
				morning's work...""",
            """	You think about
				your home and how
				you first traveled
				here to service
				the camp...""",
        ],
    )

    ThroughPage(
        uid="firstSnack",
        change=SackChange(
            minus={"money": 5},
            assign={"afternoon": True}
        ),
        page="""You stop for some food
        at a local inn.
		It costs
		{{node.change.minus['money']}} Denarii.
        You now have
        {{sack.money}} Denarii...""",
        nextNodeUid="workshop4",
        goalBoxUid=workshopBox.uid,
    )

    ThroughPage(
        uid="fromSmith",
        missTemplate="""To carry on working,
						go to {{node.goalBox.label}}""",
        page= """You're feeling more
        equipped!""",
        goalBoxUid=workshopBox.uid,
        nextNodeUid="workshop4",
    )

    NodeFork(
        uid="workshop4",
        choices={
            "smith1": """Get your tools
            sharpened""",
            "burial1": """Talk to the Burial
            Club""",
            "stone1": """Order Stone From
            the Quarry""",
        },
        hideChoices={
            "smith1": "sack.sharp==True",
            "stone1": "sack.stone==True",
            "smith1": "sack.smithAnger==True",
        },
    )
    # 2c - Carving Fork
    ThroughPage(
        uid="workshop5",
        missTemplate="""Time to get back to
        {{node.goalBox.label}}""",
        page="""Next morning, the stone
        arrives...""",
        goalBoxUid=workshopBox.uid,
        nextNodeUid="carve",
    )

    ConditionFork(
        uid="carve",
        condition="sack.sharp == True",
        trueNodeUid="goodCarve",
        falseNodeUid="badCarve",
    )

    ThroughPage(
        uid="goodCarve",
        missTemplate=	"""Stop slacking!
        Go back to {{node.goalBox.label}}""",
        page=			"""You start carving the
        tombstone. Your tools
        are nice and sharp.
		You make a detailed
		carving. Npw it's time
		to get it painted...""",
        goalBoxUid=workshopBox.uid,
        nextNodeUid="painter1",
    )

    ThroughPage(
        uid="badCarve",
        missTemplate="""Stop slacking!
						Back to {{node.goalBox.label}}!""",
        page="""You start carving the
				tombstone. Your tools
				are blunt and it looks
				a bit wrong...
				Still, you'd better get
				it painted...""",
        goalBoxUid=workshopBox.uid,
        nextNodeUid="painter1",
    )

    ThroughPage(
        uid="stoneIssue",
        missTemplate="""Stop slacking!
						Back to {{node.goalBox.label}}!""",
        page="""The stone feels damp.
        and crumbly!
        Could spoil the finish
        Let's hope the Burial
        Club don't notice!""",
        goalBoxUid=workshopBox.uid,
        nextNodeUid="carve",
        )

    # BOX III
    # 3a - Inspiration
    ThroughPage(
        uid="inspire1",
        change=SackChange(
            assign={"inspire": True}
        ),
        missTemplate="""This isn't
        {{node.goalBox.description}}!
        Go to {{node.goalBox.label}}""",
        page="""This is where the
        finished tombstone
		will be displayed...""",
        goalBoxUid=tombBox.uid,
        nextNodeUid="inspire2",
    )

    ThroughSequence(
        uid="inspire2",
        goalBoxUid=tombBox.uid,
        nextNodeUid="workshop3",
        sequence=[
            """ You've seen a Cavalry-
                man's tombstone before
                but never carved one.
                You'll need to get some
                ideas before starting...""",
            """ INVESTIGATE the stone
                carvings in the museum.
                Make a SKETCH, at the
                drawing area and then
                return to the workshop.
                """,
                ],
    )


    # 3b - Burial Club
    ThroughPage(
        uid="burial1",
        missTemplate="""This isn't
        {{node.goalBox.description}}!
        Go to {{node.goalBox.label}}""",
        nextNodeUid="burial2",
        page="""
        The Burial Club are
        making preparations for
        the tombstone to be
        displayed. You ask them
        for some help with
        research...
        """,
        goalBoxUid=tombBox.uid,
    )

    NodeFork(
        uid="burial2",
        choices={
            "drink": """Come for a drink and we
            can talk about
            Flavinus!""",
            "inspire3": """You should look for
            Flavinus' helmet
            plate...""",
        },
    )

    ThroughSequence(
        uid="inspire3",
        goalBoxUid=smithBox.uid,
        nextNodeUid="stoneCheck",
        sequence=[
            """You go to the armoury
               to look for Flavinus'
               helmet plate. Find the
               HELMET near box II,
               make a sketch then
               come back...""",
            """INVESTIGATE the spear-
                heads and weapons in
				the cabinet near Box I
				then come back...""",
            """ That's plenty of
				research for now!
				Go back to
                your workshop to
                rest up!
                """,
        ],
    )

    ThroughSequence(
            uid="drink",
            goalBoxUid=quarryBox.uid,
            nextNodeUid="buydrinks",
            sequence=[
            """They tell you that
            Flavinus was 25 years
            old and that he died
            after 7 years of service
			with the Ala Petriana
			as a standard bearer...""",
            """They tell you lots more
			about Flavinus but you
			are starting to feel a
			bit drunk and tired...""",
        ],
    )

    ThroughPage(
        uid="buydrinks",
        change=SackChange(
            #assign={"afternoon": True}
            minus={"money": 10},
        ),
        missTemplate="""Go back to the pub
        at {{node.goalBox.label}}""",
        page="""You buy drinks for
        {{node.change.minus['money']}} Denarii.
        You have {{sack.money}} Denarii.
		That's plenty of
		research for now!
		Back to the workshop.""",
        goalBoxUid=quarryBox.uid,
        nextNodeUid="stoneCheck",
    )

    ConditionFork(
        uid="stoneCheck",
        condition="sack.stone == True",
        trueNodeUid="workshop5",
        falseNodeUid="badStone",
    )

    ThroughPage(
        uid="badStone",
        missTemplate="""Stop slacking!
        Get back to {{node.goalBox.label}}""",
        page="""Back at your workshop a
        scruffy lump of stone
        is waiting with a note.
        'Heard you might need
        something for Flavinus
        all we had left, sorry'""",
        #nearly signed off with Jeremy Corbridge
        goalBoxUid=workshopBox.uid,
        nextNodeUid="stoneIssue",
        )


    ThroughPage(
        uid="painter1",
        missTemplate="""Stop slacking!
        Get back to {{node.goalBox.label}}""",
        page="""You meet the painter at
        the tomb site to put the
        finishing touches to the
		tombstone...""",
        goalBoxUid=tombBox.uid,
        nextNodeUid="painter2",
    )

    ConditionFork(
        uid="painter2",
        condition="sack.sharp == True and sack.inspire == True and sack.stone == True",
        trueNodeUid="goodPaint",
        falseNodeUid="badPaint",
    )

    ThroughPage(
        uid="goodPaint",
        change=SackChange(
            minus={"money": 15},
        ),
        missTemplate="""Stop slacking!
        Get back to {{node.goalBox.label}}""",
        page="""The finished stone
        looks stunning!
        The painter charges
        {{node.change.minus['money']}} Denarii,
        leaving you with
        {{sack.money}} Denarii...
        """,
        goalBoxUid=tombBox.uid,
        nextNodeUid="endingGood",
    )

    ThroughPage(
        uid="badPaint",
        change=SackChange(
            minus={"money": 15},
        ),
        missTemplate="""Stop slacking!
        Go back to {{node.goalBox.label}}
        to find the painter""",
        page="""
        The painter does their
        best, but it doesn't
        look good...
        The painter charges
        {{node.change.minus['money']}} Denarii,
        You have {{sack.money}} Denarii...""",
        goalBoxUid=tombBox.uid,
        nextNodeUid="endingBad",
    )

    # 3d - Endings
    ThroughSequence(
        uid="endingGood",
        goalBoxUid=tombBox.uid,
        nextNodeUid="reward",
        sequence=[
			"""	You're now ready for
				the unveiling...""",
            """	That evening, the
				Cavalrymen and members
				of the Burial Club
                arrive to unveil the
				tombstone...""",
            """'Flavinus is well-
				represented - the Gods
				and all that pass by
				his tomb will see what
				a great soldier he was.'
				they say...""",
        ]
    )

    ThroughPage(
        uid="reward",
        change=SackChange(
            plus={"money": 100},
        ),
        page="""
        The soldiers pay you a
        bonus of {{node.change.plus['money']}} Denarii
        and give you a
        LAUREL WREATH!
        """,
        goalBoxUid=tombBox.uid,
        nextNodeUid="ending",
    )

    ThroughSequence(
        uid="endingBad",
        goalBoxUid=tombBox.uid,
        nextNodeUid="refund",
        sequence=[
            """You're now ready for
            the unveiling...""",
            """That evening, the
            Cavalrymen and members
            of the Burial Club
            arrive to unveil the
            tombstone...""",
            """The soldiers tell you
			that Flavinus is wearing
			the wrong helmet and
			that his horse is
			wonky-looking.
            They refuse to pay...""",
        ],
    )

    ThroughPage(
        uid="refund",
        change=SackChange(
            minus={"money": 50},
        ),
        page="""
            The soldiers demand a
            refund of
            {{node.change.minus['money']}} Denarii.
            You now have
            {{sack.money}} Denarii.
            """,
        goalBoxUid=tombBox.uid,
        nextNodeUid="ending",
    )

    # BOX IV
    # 4a Quarry

    ThroughPage(
        uid="stone1",
        missTemplate="""This isn't
        {{node.goalBox.description}}!
        Go to {{node.goalBox.label}}""",
        page="""You are on an East-West
				road used for supplying
				the fort. There are a
				number of shops here...""",
        goalBoxUid=quarryBox.uid,
        nextNodeUid="stone2",
    )

    ThroughPage(
        uid="stone2",
        change=SackChange(
            assign={"stone": True},
            minus={"money": 50}
        ),
        page="""You meet the quarryman
				and place an order of
                stone for tomorrow.
				It costs {{node.change.minus['money']}} Denarii,
				leaving you with
				{{sack.money}} Denarii.""",
        goalBoxUid=quarryBox.uid,
        nextNodeUid="stoneFork",
    )

    NodeFork(
        uid="stoneFork",
        choices={
            "stoneAlone": """PRETEND to CARRY
            the stone
            yourself""",
            "stoneDonkey": """Hire a donkey and
            PRETEND to RIDE it
            back!""",
        }
    )

    ThroughPage(
        uid="stoneAlone",
        goalBoxUid=workshopBox.uid,
        page="""What strength!
        You carried the
        stone yourself!""",
        nextNodeUid="workshop1"
    )

    ThroughPage(
        uid="stoneDonkey",
        goalBoxUid=smithBox.uid,
        change=SackChange(
            minus={"money": 5}
        ),
        missTemplate="""Come on, back to
        {{node.goalBox.description}}!
        Go to {{node.goalBox.label}}""",
        page="""You hired a donkey to
        carry the stone, now
        RIDE the donkey back to
		the workshop. It cost
		{{node.change.minus['money']}} Denarii, leaving you
        with {{sack.money}} Denarii.""",
        nextNodeUid="stoneTime"
    )

    ConditionFork(
        uid="stoneTime",
        condition="sack.afternoon == False",
        trueNodeUid="workshop1",
        falseNodeUid="fromSmith",
    )

    ThroughPage(
        uid="ending",
        page="""
        You completed the game
        with {{sack.money}} Denarii!
        Return to {{node.goalBox.label}}
        to try again or visit
        another museum to play
        more MileCastles!
        """,
        nextNodeUid="landing",
        goalBoxUid=entranceBox.uid,
    )

def run():
    emulator = ConsoleSiteEmulator(story=story)
    emulator.run()


if __name__ == "__main__":
    run()




