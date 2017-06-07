import agnostic
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
        "points": 0,
        "smithAnger": False,
        "stone": False,
        "sharp": False,
        "inspire": False,
        "afternoon": False,
    }
)
agnostic.collect()

with story:
    # populate with boxes

    smithBox = Box(uid="1", label="Box I", description="the Blacksmith")
    agnostic.collect()
    workshopBox = Box(uid="2", label="Box II", description="the Workshop")
    agnostic.collect()
    tombBox = Box(uid="3", label="Box III", description="the Tomb")
    agnostic.collect()
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
    agnostic.collect()

    # 1b Blacksmith am/pm

    ThroughPage(
        uid="smith1",
        missTemplate="""This isn't the
                        blacksmith's workshop!
                        Go to {{node.goalBox.label}}""",
        page="""You walk across the fort
                to the blacksmith's
                workshop. A sign says
                'Half day opening today'.""",
        goalBoxUid=smithBox.uid,
        nextNodeUid="sharpening",
    )
    agnostic.collect()

    ConditionFork(
        uid="sharpening",
        condition="sack.afternoon == True",
        trueNodeUid="sharpeningSuccess",
        falseNodeUid="sharpeningFailure",
    )
    agnostic.collect()

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
    agnostic.collect()

    ThroughPage(
        uid="sharpened",
        missTemplate="""This isn't the
                        blacksmith's workshop!
                        Go to {{node.goalBox.label}}""",
        # 2345678901234567890123456| 26 char limit
        page="""Look at the tools in the
                display and PRETEND to
                sharpen a spearhead.
                Now your tools are sharp,
                you can add lots of
                detail to the carving!""",
        # superfluous {{story.nodes.fromSmith.getGoalBox(story).description}} to the workshop.",
        goalBoxUid=smithBox.uid,
        nextNodeUid="fromSmith",
    )
    agnostic.collect()

    # Now our sharpening fail
    ThroughPage(
        uid="sharpeningFailure",
        missTemplate="""This isn't the
                        blacksmith's workshop!
                        Go to {{node.goalBox.label}}""",
        change=SackChange(
            assign={"smithAnger": True},
        ),
        # 2345678901234567890123456| 26 char limit
        page="""The Blacksmith is furious
                'You're banned...no sharp
                tools for you!'""",
        goalBoxUid=smithBox.uid,
        nextNodeUid="workshop1",
    )
    agnostic.collect()

    # BOX II

    # 2a Morning / First Workshop Fork

    ThroughPage(
        uid="workshop1",
        missTemplate="Begin work at {{node.goalBox.label}}!",
        page="""You are in your workshop.
                It's early morning but
                you don't have long to
                complete the tombstone.""",
        goalBoxUid=workshopBox.uid,
        nextNodeUid="workshop2",
    )
    agnostic.collect()

    NodeFork(
        uid="workshop2",
        choices={
            "smith1": """Sharpen your tools at the
                        blacksmith's""",
            "stone1": """Go outside to order stone
                        from the quarry""",
            "inspire1": """Seek inspiration""",
        },
        hideChoices={
            "smith1": "sack.sharp==True",
            "stone1": "sack.stone==True",
            "smith1": "sack.smithAnger==True",
        },
    )
    agnostic.collect()

    # 2b Afternoon / Second Workshop Fork

    ThroughPage(
        uid="workshop3",
        goalBoxUid=workshopBox.uid,
        nextNodeUid="firstSnack",
        page="""A good morning's work!
                You think about your home
                and how you first
                traveled here with the
                army to service the camp.""",
    )
    agnostic.collect()

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
        You have {{sack.money}} denarii left.
        """,
        goalBoxUid=workshopBox.uid,
    )
    agnostic.collect()

    ThroughPage(
        uid="fromSmith",
        missTemplate="""To carry on working,
                        go to {{node.goalBox.label}}""",
        page="You're feeling equipped!",
        goalBoxUid=workshopBox.uid,
        nextNodeUid="workshop4",
    )
    agnostic.collect()

    NodeFork(
        uid="workshop4",
        choices={
            "smith1": "Sharpen your tools",
            "stone1": "Order stone!",
            "burial1": "Meet Burial Club"
        },
        hideChoices={
            "smith1": "sack.sharp==True",
            "stone1": "sack.stone==True",
            "smith1": "sack.smithAnger==True",
        },
    )
    agnostic.collect()

    # 2c - Carving Fork

    ThroughPage(
        uid="workshop5",
        missTemplate="""Time to get carving at
                        the workshop! Go to
                        {{node.goalBox.label}}""",
        page="""
        Next morning, the stone
        block arrives.
        """,
        goalBoxUid=workshopBox.uid,
        nextNodeUid="carve",
    )
    agnostic.collect()

    ConditionFork(
        uid="carve",
        condition="sack.sharp == True",
        trueNodeUid="goodCarve",
        falseNodeUid="badCarve",
    )
    agnostic.collect()

    ThroughPage(
        uid="goodCarve",
        missTemplate="""Stop slacking!
                    Back to {{node.goalBox.label}}""",
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
    agnostic.collect()

    ThroughPage(
        uid="badCarve",
        missTemplate="""Stop slacking!
                    Back to {{node.goalBox.label}}""",
        # 2345678901234567890123456| 26 char limit
        page="""You start carving the
                tombstone. Your tools are
                blunt and it looks wonky.
                Still, better get it
                painted.""",
        goalBoxUid=workshopBox.uid,
        nextNodeUid="painter1",
    )
    agnostic.collect()

    # BOX III

    # 3a - Inspiration

    ThroughPage(
        uid="inspire1",
        change=SackChange(
            assign={"inspire": True}
        ),
        missTemplate="""This isn't the tomb site!
                        Go to {{node.goalBox.label}}""",
        page="""This is where the
                finished tombstone
                will be displayed.""",
        goalBoxUid=tombBox.uid,
        nextNodeUid="inspire2",
    )
    agnostic.collect()

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
    agnostic.collect()

    # 3b - Burial Club

    ThroughPage(
        uid="burial1",
        missTemplate="""This isn't the tomb site!
                        Go to {{node.goalBox.label}}""",
        # 2345678901234567890123456| 26 char limit
        page="""
        The Burial Club are
        making preparations
        for the tombstone to be
        displayed. You ask them
        for some help with
        research.
        """,
        goalBoxUid=tombBox.uid,
        nextNodeUid="burial2",
    )
    agnostic.collect()

    NodeFork(
        uid="burial2",
        choices={
            "drink": """Come with us for a
                        drink. We can tell you
                        stories!!""",
            "inspire3": """Look at Flavinus'
                        helmet plate""",
        },
    )
    agnostic.collect()

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
            """ INVESTIGATE the spear
                heads and weapons in
                the case near Box I then
                come back.""",
            """ That's plenty of research
                for now! Go back to
                your workshop to rest up!
                """,
        ],
    )
    agnostic.collect()

    ThroughSequence(
        uid="drink",
        goalBoxUid=smithBox.uid,
        nextNodeUid="buydrinks",
        sequence=[
            """ They tell you Flavinus
                was 25 years old and he
                died after 7 years of
                service with Ala Petriana
                as a standard bearer.""",
            """ They tell you lots more
                about Flavinus but you
                are starting to get a bit
                drunk and tired...""",
            # seperated this from logic with a thru page
        ],
    )
    agnostic.collect()

    # Seperated this from story.node.drink sequence so logic works
    ThroughPage(
        uid="buydrinks",
        change=SackChange(
            minus={"money": 10},
        ),
        # Maybe have something that refers to beign in the pub?
        # missTemplate =  "Get back to the pub! goto {{node.goalBox.label}}",
        missTemplate="""Stop slacking!
                        Back to {{node.goalBox.label}}""",
        page="""
            You buy drinks for {{node.change.minus['money']}}
            Denarii. You have {{sack.money}}
            Denarii left. That's
            plenty of research for
            now! Go back to your
            workshop to rest up!""",
        goalBoxUid=tombBox.uid,
        nextNodeUid="workshop5",
    )
    agnostic.collect()

    # 3c - Painter fork


    ThroughPage(
        uid="painter1",
        missTemplate="""Stop slacking!
                        Back to {{node.goalBox.label}}""",
        page="""You meet the painter at
             the site later to put the
             finishing touches to the
             tombstone...  """,
        goalBoxUid=tombBox.uid,
        nextNodeUid="painter2",
    )
    agnostic.collect()

    ConditionFork(
        uid="painter2",
        # added inspire logic so looking for inspiration makes a difference?
        condition="sack.sharp == True and sack.inspire == True",
        trueNodeUid="goodPaint",
        falseNodeUid="badPaint",
    )
    agnostic.collect()

    ThroughPage(
        uid="goodPaint",
        change=SackChange(
            minus={"money": 15},
        ),
        missTemplate="""Stop slacking!
                     Back to {{node.goalBox.label}}""",
        page="""The finished stone looks
                stunning! The painter
                charges {{node.change.minus['money']}} Denarii,
                leaving you with {{sack.money}}.
        """,
        goalBoxUid=tombBox.uid,
        nextNodeUid="endingGood",
    )
    agnostic.collect()

    ThroughPage(
        uid="badPaint",
        change=SackChange(
            minus={"money": 15},
        ),
        missTemplate="""Stop slacking!
                        Back to {{node.goalBox.label}}
                        to find the painter""",
        page="""The painter does their
                best, but it looks bad.
                The painter charges
                {{node.change.minus['money']}} Denarii,
                leaving you with {{sack.money}}.""",
        goalBoxUid=tombBox.uid,
        nextNodeUid="endingBad",
    )
    agnostic.collect()

    # 3d - Endings

    ThroughSequence(
        uid="endingGood",
        goalBoxUid=tombBox.uid,
        nextNodeUid="reward",
        sequence=[
            """ You're now ready for the
                unveiling this evening.""",
            """ That evening, the
                Cavalrymen and members of
                the Burial Club arrive to
                unveil the tombstone...""",
            """ 'Flavinus is well-
                represented, the gods and
                all that pass will see
                what a soldier he was.'
                they say.""",
        ]
    )
    agnostic.collect()
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
    agnostic.collect()

    ThroughSequence(
        uid="endingBad",
        goalBoxUid=tombBox.uid,
        nextNodeUid="refund",
        sequence=[
            """ You're now ready for the
                unveiling this evening.""",
            """ That evening, the
                Cavalrymen and members of
                the Burial Club arrive to
                unveil the tombstone...""",
            """ The soldiers tell you
                Flavinus is wearing the
                wrong helmet and that his
                horse is wonky-looking.
                They refuse to pay you.""",
        ],
    )
    agnostic.collect()

    ThroughPage(
        uid="refund",
        change=SackChange(
            minus={"money": 50},
        ),
        page="""
            The soldiers demand a
            refund of {{node.change.minus['money']}} denarii,
            You have {{sack.money}}
            Denarii left.
            """,
        goalBoxUid=tombBox.uid,
        nextNodeUid="ending",
    )
    agnostic.collect()

    # BOX IV

    # 4a Quarry

    ThroughPage(
        uid="stone1",
        missTemplate="""This isn't the quarry!
                        Go to {{node.goalBox.label}}""",
        page="""You are on an East-West
                road used for supplying
                the fort. There are a
                number of shopfronts here""",
        goalBoxUid=quarryBox.uid,
        nextNodeUid="stone2",
    )
    agnostic.collect()

    ThroughPage(
        uid="stone2",
        change=SackChange(
            assign={"stone": True},
            minus={"money": 50}
        ),
        page="""You meet the quarry
                manager and place an
                order for stone to
                arrive tomorrow. It
                costs {{node.change.minus['money']}} Denarii,
                leaving you with
                {{sack.money}} Denarii.""",
        goalBoxUid=quarryBox.uid,
        nextNodeUid="stoneFork",
    )
    agnostic.collect()

    NodeFork(
        uid="stoneFork",
        # Note the difference between getGoalBox(story).description and
        # getGoalBox(story).label, it means you can tell people to go to a box
        # to do something without it being associated with the description
        # so you dont think youre hiring a donkey from the grumpy blacksmith
        choices={
            "stoneAlone": """PRETEND to carry the
                            stone yourself to""",
            "stoneDonkey": """Go to {{story.nodes.stoneDonkey.getGoalBox(story).label}},
                            to hire a donkey and
                            PRETEND to ride it back
                            to the workshop.""",
        }
    )
    agnostic.collect()

    ThroughPage(
        uid="stoneAlone",
        goalBoxUid=workshopBox.uid,
        page="""What strength!
                You carried the stone
                yourself.
        """,
        nextNodeUid="workshop1"
    )
    agnostic.collect()

    ThroughPage(
        uid="stoneDonkey",
        goalBoxUid=smithBox.uid,
        change=SackChange(
            minus={"money": 5}
        ),
        page="""You hired a donkey to
                carry the stone, now ride
                the donkey back to the
                workshop. It costs
                {{node.change.minus['money']}} Denarii,
                leaving you with
                {{sack.money}} Denarii.""",
        nextNodeUid="stoneTime"
    )
    agnostic.collect()

    ConditionFork(
        uid="stoneTime",
        condition="sack.afternoon == False",
        trueNodeUid="workshop1",
        falseNodeUid="fromSmith",
    )
    agnostic.collect()

    ThroughPage(
        uid="ending",
        page="""You completed your game
        with a total of
        {{sack.money}} Denarii
        Can you do better?
        Return to {{node.goalBox.label}} to try
        again or visit another
        museum to play more
        MileCastles!""",
        nextNodeUid="landing",
        goalBoxUid=entranceBox.uid,
        # goalBoxUid = tombBox.uid,
    )
    agnostic.collect()

def run():
    from regimes.console import ConsoleSiteEmulator
    emulator = ConsoleSiteEmulator(story=story)
    emulator.run()

if __name__ == "__main__":
    run()