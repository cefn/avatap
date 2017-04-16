from consoleEngine import ConsoleSiteEmulator
from milecastles import Story, Box, ThroughPage, ThroughSequence, ConditionFork, NodeFork, SackChange

# inspects the module to figure out the story name (e.g. corbridge)
storyName = __name__.split(".")[-1]

# create story
story = Story(
    uid=storyName,
    # choose an alternative startNodeUid and startSack for debugging
    # startNodeUid = "stoneFork",
    startNodeUid="landing",
    startSack={
        "money": 100,
        "points": 0,
        "smithAnger": False,
        "stone": False,
        "sharp": False,
        "inspire": False,
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
            # 2345678901234567890123456
            """ Welcome to Milecastles!
                Look for numbered boxes
                and tap your card to
                progress the story!""",
            """ You are a stonemason
                working at the military
                base at Corbridge.""",
            """ Your quest is to get
                materials, tools and
                inspiration to complete
                the tombstone.""",
            """ You have an advance of
                {{sack.money}} Denarii
                for materials.
                Spend it wisely!""",
        ],
    )

    # 1b Blacksmith am/pm

    ThroughPage(
        uid="smith1",
        missTemplate="This isn't the blacksmith! {{node.goalBox.label}}",
        page="You walk across the fort to the blacksmith's workshop. The sign says 'Half day opening today'.",
        goalBoxUid=smithBox.uid,
        nextNodeUid="sharpening",
    )

    ConditionFork(
        uid="sharpening",
        condition="sack.afternoon == True",
        trueNodeUid="sharpeningSuccess",
        falseNodeUid="sharpeningFailure",
    )
    # changed this to ThroughPage as logic wont work so well in a ThroughSequence
    ThroughPage(
        uid="sharpeningSuccess",
        change=SackChange(
            # may need to include trigger condition in case you get here again with sharp tools
            trigger="sack.sharp == False",
            # it's false so lets make it True because blacksmith is not grumpy
            assign={"sharp": True},
            plus={"points": 1},
            minus={"money": 15},
        ),
        goalBoxUid=smithBox.uid,
        page="""
        {% if node.change.triggered %}
            {% if node.change.completed %}
                It's now the afternoon
                and the blacksmith is
                ready for you.Sharpening
                costs {{node.change.minus['money']}} denarii.
                You now have {{sack.money}} denarii.
            {% else %}
                You don't have enough money to sharpen your tools
            {% endif %}
        {% else %}
            You already sharpened your tools
        {% endif %}
        """,
        nextNodeUid="sharpened",
    )

    ThroughPage(
        uid="sharpened",
        missTemplate="This isn't the blacksmith! {{node.goalBox.label}}",
        # 2345678901234567890123456| 26 char limit
        page="""
        Look at the tools in the
        display and PRETEND to
        sharpen a spearhead.
        Now your tools are sharp,
        you can add lots of detail
        to the carving!
        """,
        # superfluous {{story.nodes.fromSmith.getGoalBox(story).description}} to the workshop.",
        goalBoxUid=smithBox.uid,
        nextNodeUid="fromSmith",
    )
    # Now our sharpening fail
    ThroughPage(
        uid="sharpeningFailure",
        missTemplate="This isn't the blacksmith! {{node.goalBox.label}}",
        change=SackChange(
            assign={"smithAnger": True},
        ),
        # 2345678901234567890123456| 26 char limit
        page="""
        The Blacksmith is furious!
        'You're banned... no sharp
        tools for you!'
        """,
        goalBoxUid=smithBox.uid,
        nextNodeUid="workshop1",
    )

    # BOX II

    # 2a Morning / First Workshop Fork

    ThroughPage(
        uid="workshop1",
        missTemplate="To begin work go to {{node.goalBox.label}}",
        page="""
        You are in your workshop.
        It's early in the morning
        but you don't have long to
        complete the tombstone.
        """,
        goalBoxUid=workshopBox.uid,
        nextNodeUid="workshop2",
    )

    NodeFork(
        uid="workshop2",
        choices={
            "smith1": "Get your tools sharpened at the blacksmith",
            "stone1": "Go outside to order stone from the quarry",
            "inspire1": "Look for inspiration",
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
            " You've done a good morning's work!",
            """You think about your home
            and how you first traveled
            here with the army to
            service the camp.
            """,
        ],
    )

    ThroughPage(
        uid="firstSnack",
        change=SackChange(
            minus={"money": 5},
            plus={"points": 1},
            assign={"afternoon": True}
        ),
        nextNodeUid="workshop4",
        # use {{node.change.minus['money']}} to pull in the actual money you will spend
        # helps test against the logic
        page="""
        You stop for some food
        at a local inn. It costs
        {{node.change.minus['money']}} denarii.
        You now have {{sack.money}} denarii left.
        """,
        goalBoxUid=workshopBox.uid,
    )

    ThroughPage(
        uid="fromSmith",
        missTemplate="To carry on working, go to {{node.goalBox.label}}",
        page="You're feeling more equipped!",
        goalBoxUid=workshopBox.uid,
        nextNodeUid="workshop4",
    )

    NodeFork(
        uid="workshop4",
        choices={
            "smith1": "Get your tools sharpened",
            "stone1": "I need to order stone!",
            "burial1": "Talk to Burial Club"
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
        missTemplate="Time to get carving at the workshop! {{node.goalBox.label}}",
        page="""
        Next morning, the stone
        block arrives.
        """,
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
        missTemplate="Stop slacking! Back to {{node.goalBox.label}}",
        page="""
        You start carving the
        tombstone. Your tools are
        incredibly sharp and you
        make a detailed carving.
        Time to get it painted.
        """,
        goalBoxUid=workshopBox.uid,
        nextNodeUid="painter1",
    )

    ThroughPage(
        uid="badCarve",
        missTemplate="Stop slacking! Back to {{node.goalBox.label}}",
        # 2345678901234567890123456| 26 char limit
        page="""
        You start carving the
        tombstone. Your tools are
        blunt and it looks wonky..
        Still, better get it
        painted.
        """,
        goalBoxUid=workshopBox.uid,
        nextNodeUid="painter1",
    )

    # BOX III

    # 3a - Inspiration

    ThroughPage(
        uid="inspire1",
        change=SackChange(
            assign={"inspire": True}
        ),
        missTemplate="This isn't the tomb site! {{node.goalBox.label}}",
        page="This is where the finished tombstone will be displayed.",
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
                ideas before starting.""",
            """ INVESTIGATE the stone
                carvings in this part of
                the museum. Make some
                SKETCHES, at the drawing
                area then comeback.
                """,
        ],
    )

    # 3b - Burial Club

    ThroughPage(
        uid="burial1",
        missTemplate="This isn't the tomb site! {{node.goalBox.label}}",
        # 2345678901234567890123456| 26 char limit
        page="""
        The Burial Club are making
        preparations for the
        tombstone to be displayed.
        You ask them for some help
        with research.
        """,
        goalBoxUid=tombBox.uid,
        nextNodeUid="burial2",
    )

    NodeFork(
        uid="burial2",
        choices={
            "drink": "Come with us for a drink and we can tell you stories!!",
            "inspire3": "You should look at Flavinus' helmet plate",
        },
    )

    ThroughSequence(
        uid="inspire3",
        # QUESTION
        # Wondered if this should still be at box II? Seem to be there all the time...
        # And seems weird to say go back to the workshop which is where we are already
        # Maybe this should be Box 3?
        goalBoxUid=workshopBox.uid,
        nextNodeUid="workshop5",
        sequence=[
            """ You go to the armoury
                to look for Flavinus'
                helmet plate. Find the
                HELMET near box II, make
                a sketch then come back.""",
            """ INVESTIGATE the spearheads
                and weapons in the case
                near Box I then come back.""",
            """ That's plenty of research
                for now! Go back to
                your workshop to rest up!
                """,
        ],
    )

    ThroughSequence(
        uid="drink",
        goalBoxUid=smithBox.uid,
        nextNodeUid="buydrinks",
        sequence=[
            """ They tell you that Flavinus
                was 25 years old and he died
                after 7 years of service with
                the Ala Petriana as a standard
                bearer.""",
            """ They tell you lots more about
                Flavinus but you are starting
                to get a bit drunk and tired...""",
            # seperated this from logic with a thru page
        ],
    )

    # Seperated this from story.node.drink sequence so logic works
    ThroughPage(
        uid="buydrinks",
        change=SackChange(
            minus={"money": 10},
        ),
        # Maybe have something that refers to beign in the pub?
        # missTemplate =  "Get back to the pub! goto {{node.goalBox.label}}",
        missTemplate="Stop slacking! Back to {{node.goalBox.label}}",
        page="""
            You buy drinks for {{node.change.minus['money']}} Denarii.
            You have {{sack.money}} Denarii left.
            That's plenty of research for now!
            Go back to your workshop to rest up!""",
        goalBoxUid=tombBox.uid,
        nextNodeUid="workshop5",
    )

    # 3c - Painter fork


    ThroughPage(
        uid="painter1",
        missTemplate="Stop slacking! Back to {{node.goalBox.label}}",
        page="You meet the painter at the site later to put the finishing touches to the tombstone...  ",
        goalBoxUid=tombBox.uid,
        nextNodeUid="painter2",
    )

    ConditionFork(
        uid="painter2",
        # added inspire logic so looking for inspiration makes a difference?
        condition="sack.sharp == True and sack.inspire == True",
        trueNodeUid="goodPaint",
        falseNodeUid="badPaint",
    )

    ThroughPage(
        uid="goodPaint",
        change=SackChange(
            minus={"money": 15},
        ),
        missTemplate="Stop slacking! Back to {{node.goalBox.label}}",
        page="""
        The finished stone looks
        stunning! The painter
        charges {{node.change.minus['money']}} Denarii,
        leaving you with {{sack.money}}.
        """,
        goalBoxUid=tombBox.uid,
        nextNodeUid="endingGood",
    )

    ThroughPage(
        uid="badPaint",
        change=SackChange(
            minus={"money": 15},
        ),
        missTemplate="""
        Stop slacking! Back to {{node.goalBox.label}}
        to find the painter""",
        page="""The painter does their best,
        but it doesn't look great.
        The painter charges {{node.change.minus['money']}} Denarii, leaving you
        with {{sack.money}}.""",
        goalBoxUid=tombBox.uid,
        nextNodeUid="endingBad",
    )

    # 3d - Endings

    ThroughSequence(
        uid="endingGood",
        goalBoxUid=tombBox.uid,
        nextNodeUid="reward",
        sequence=[
            """You're now ready for the
            unveiling this evening.""",
            """That evening, the Cavalrymen
            and members of the Burial
            Club arrive to unveil the
            tombstone...""",
            """'Flavinus is well-represented,
            the gods and all that pass
            will see what a soldier
            he was.' they say.""",
        ]
    )
    # Added the node.change.plus code so checks against logic

    ThroughPage(
        uid="reward",
        change=SackChange(
            plus={"money": 100},
        ),
        page="""
        The soldiers pay you a
        bonus of {{node.change.plus['money']}} denarii and
        give you a LAUREL WREATH!
        """,
        goalBoxUid=tombBox.uid,
        nextNodeUid="ending",
    )

    ThroughSequence(
        uid="endingBad",
        goalBoxUid=tombBox.uid,
        nextNodeUid="refund",
        sequence=[
            """ You're now ready for the
                unveiling this evening.""",
            """ That evening, the Cavalrymen
                and members of the Burial
                Club arrive to unveil the
                tombstone...""",
            """ The soldiers tell you that
                Flavinus is wearing the
                wrong helmet and that his
                horse is wonky looking.
                They refuse to pay you.""",
        ],
    )

    ThroughPage(
        uid="refund",
        change=SackChange(
            minus={"money": 50},
        ),
        page="""
            The soldiers demand a refund
            of {{node.change.minus['money']}} denarii. You now
            have {{sack.money}} Denarii.
            """,
        goalBoxUid=tombBox.uid,
        nextNodeUid="ending",
    )

    # BOX IV

    # 4a Quarry

    ThroughPage(
        uid="stone1",
        missTemplate="This isn't the quarry! {{node.goalBox.label}}",
        page="You are on an East-West road used for supplying the fort. There are a number of shopfronts here.",
        goalBoxUid=quarryBox.uid,
        nextNodeUid="stone2",
    )

    ThroughPage(
        uid="stone2",
        change=SackChange(
            assign={"stone": True},
            minus={"money": 50}
        ),
        page="You meet the quarry manager and place an order for stone to arrive tomorrow. It costs {{node.change.minus['money']}} Denarii, leaving you with {{sack.money}} Denarii.",
        goalBoxUid=quarryBox.uid,
        nextNodeUid="stoneFork",
    )

    NodeFork(
        uid="stoneFork",
        # Note the difference between getGoalBox(story).description and
        # getGoalBox(story).label, it means you can tell people to go to a box
        # to do something without it being associated with the description
        # so you dont think youre hiring a donkey from the grumpy blacksmith
        choices={
            "stoneAlone": "PRETEND to carry the stone yourself back to {{story.nodes.stoneAlone.getGoalBox(story).description}}",
            "stoneDonkey": "Go to {{story.nodes.stoneDonkey.getGoalBox(story).label}}, to hire a donkey and PRETEND to ride it back to the workshop.",
        }
    )

    ThroughPage(
        uid="stoneAlone",
        goalBoxUid=workshopBox.uid,
        page="""What strength!
        You carried the stone yourself
        """,
        nextNodeUid="workshop1"
    )

    ThroughPage(
        uid="stoneDonkey",
        goalBoxUid=smithBox.uid,
        change=SackChange(
            minus={"money": 5}
        ),
        page="You hired a donkey to carry the stone, now ride the donkey back to the workshop. It costs {{node.change.minus['money']}} Denarii, leaving you with {{sack.money}} Denarii.",
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
        You completed your game
        with a total of {{sack.money}} Denarii
        Can you do better?
        Return to {{node.goalBox.label}} to try
        again or visit another
        museum to play more
        MileCastles!
        """,
        nextNodeUid="landing",
        goalBoxUid=entranceBox.uid,
        # goalBoxUid = tombBox.uid,
    )


def run():
    print("Loading emulator")
    emulator = ConsoleSiteEmulator(story=story)
    print("Running Emulator")
    emulator.run()


if __name__ == "__main__":
    run()
